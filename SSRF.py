from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO
from urllib.parse import urlparse, unquote
import re, urllib.request, base64, socket, json

def research_url(url):

    research_results = {}

    research_results["url"] = url

    try:
        web_request = urllib.request.urlopen(url)
        bytes = web_request.read()
        research_results["html"] = bytes.decode("utf8")
        research_results["ip"] = socket.gethostbyname(urlparse(web_request.geturl()).hostname)
        research_results["http_status"] = web_request.status
        web_request.close()
    except:
        research_results["error"] = "url exception"
        
    if not "error" in research_results:
    
        title_search = re.search('<title>(.*)</title>', research_results["html"], re.IGNORECASE)
        if title_search:
            research_results["title"] = title_search.group(1)
        else:
            research_results["title"] = '(none)'
            
        rendertron_url = "https://render-tron.appspot.com/screenshot/{}/?width=1200".format(url)
        rendertron_request = urllib.request.urlopen(rendertron_url)
        screenshot_bytes = rendertron_request.read()
        rendertron_request.close()
        research_results["screenshot_b64"] = base64.b64encode(screenshot_bytes)
        
        ipapi_url = "http://ip-api.com/json/{}".format( research_results["ip"] )
        ipapi_request = urllib.request.urlopen(ipapi_url)
        ipapi_json = json.loads(ipapi_request.read().decode(ipapi_request.info().get_param('charset') or 'utf-8'))
        research_results["ip_country"] = ipapi_json["country"]
        research_results["ip_region"] = ipapi_json["regionName"]
        research_results["ip_org"] = ipapi_json["org"]
    
    return research_results
  

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        
        path = self.path.split('?')[0]
        
        if path == "/research":
            query = urlparse(self.path).query
            query_components = dict(qc.split("=") for qc in query.split("&"))
            url = query_components["url"]
            
            if url:
                research_results = research_url( unquote(url) )


        self.wfile.write(b'''
<html>
	<head>
		<title>Stealth Site Research Function</title>
        <style>
            body {
                background:#222; 
                color:#fff;
            }
            input.url {
                width: 500px;
                background: #333;
                color: #fff;
                border: 1px solid #fff;
                border-radius: 3px;
                padding: 3px;
            }
            input.submit {
                padding: 3px 10px;
                border-radius: 3px;
                cursor: pointer;
            }
            p.warning {
                color: orange;
                margin-top: 50px;
                font-family: sans-serif;
                font-size: small;
            } 
            img.screenshot {
                width: 600px;
            }
            textarea.sourcecode {
                width: 600px;
                height: 2150px;
                background:#222; 
                color:#fff;
            }
            td.results {
                padding: 1px 10px;
                vertical-align: top;
            }
            td.results:first-child {
                text-align: right;
            }
        </style>
	</head>
	<body>
		<h2>Stealth Site Research Function</h2>
		<p>Enter a URL to investigate. Web requests are routed from our server through a Tor gateway, so your opsec is preserved.</p>
		<pre>
Stealth Site Research Function Architecture:
		
                  +--------------AWS-------------+
                  |                              |
+-----+             +----------+     +---------+             +---------------+
| You |-----------> |   Our    +---> | Our Tor |-----------> |  Site you're  |
|     |             |  Server  |     | Gateway |             | investigating |
+-----+             +----------+     +---------+             +---------------+
		</pre>
        <p>Try it out!</p>
        <form action="/research" method="get">
            <input type="text" class="url" name="url" placeholder="http://..."></input>
            <input type="submit" class="submit" value="Research"></input>
        </form>
        ''')
        
        try:
            self.wfile.write(b'<div id="results"> ')
            self.wfile.write(b'<h3 class="results">Results</h3>')
            if "error" in research_results:
                self.wfile.write(b'<p> class="error">Error fetching url - it is likely down<p>')
            else:
                self.wfile.write(str.encode('''
                    <table class="results">
                        <tr><td class="results">URL</td><td>{url}</td></tr>
                        <tr><td class="results">HTTP Status</td><td>{http_status}</td></tr>
                        <tr><td class="results">IP</td><td>{ip}</td></tr>
                        <tr><td class="results">Location</td><td>{region}, {country}</td></tr>
                        <tr><td class="results">Org</td><td>{org}</td></tr>
                        <tr><td class="results">Screenshot</td><td> <img class="screenshot" src="data:image/png;base64,{screenshot_b64}"/></td></tr>
                        <tr><td class="results">HTML Source</td><td><textarea class="sourcecode" readonly>{html}</textarea></td></tr>
                    </table>
                '''.format(
                    url = research_results["url"],
                    http_status = research_results["http_status"],
                    ip = research_results["ip"],
                    region = research_results["ip_region"],
                    country = research_results["ip_country"],
                    org = research_results["ip_org"],
                    screenshot_b64 = research_results["screenshot_b64"].decode(),
                    html = research_results["html"]
                )))
            self.wfile.write(b'</div>')
        except UnboundLocalError:
            pass
        #except:
        #    self.wfile.write(b'''<p>Unhandled exception, boo</p>''')
        
        self.wfile.write(b'''
        <p class="warning">&#9888; This application is minimally-functional, trivially exploitable, and does not actually use Tor. You MUST decomission this server after the lab!</p>
	</body>
</html>			
		''')
		


httpd = HTTPServer(('', 8000), SimpleHTTPRequestHandler)
httpd.serve_forever()