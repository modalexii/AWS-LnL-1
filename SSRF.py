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
        try:
            rendertron_request = urllib.request.urlopen(rendertron_url)
            screenshot_bytes = rendertron_request.read()
            rendertron_request.close()
            research_results["screenshot_b64"] = base64.b64encode(screenshot_bytes)
        except:
            research_results["screenshot_b64"] = b'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' # broken image
        
        try:
            ipapi_url = "http://ip-api.com/json/{}".format( research_results["ip"] )
            ipapi_request = urllib.request.urlopen(ipapi_url)
            ipapi_json = json.loads(ipapi_request.read().decode(ipapi_request.info().get_param('charset') or 'utf-8'))
            research_results["ip_country"] = ipapi_json["country"]
            research_results["ip_region"] = ipapi_json["regionName"]
            research_results["ip_org"] = ipapi_json["org"]
        except:
            research_results["ip_country"] = 'unknown'
            research_results["ip_region"] = 'unknown'
            research_results["ip_org"] = 'unknown'
    
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
                max-width: 600px;
            }
            textarea.sourcecode {
                width: 600px;
                height: 150px;
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
                self.wfile.write(b'<p class="error">Error fetching url - it is likely down<p>')
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