import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        q = parse_qs(urlparse(self.path).query)
        item = q.get("id", ["1"])[0]
        if "'" in item or '"' in item:
            body = "You have an error in your SQL syntax near ''1''' (mysql)"
            if "SLEEP" in item or "sleep" in item:
                time.sleep(6)
            self.send_response(200)
        elif "1'='2" in item or "1=2" in item:
            body = "no rows"
            self.send_response(200)
        else:
            body = "<h1>item 1</h1><p>price 100</p>" * 20
            self.send_response(200)
        data = body.encode()
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


HTTPServer(("127.0.0.1", 8765), H).serve_forever()
