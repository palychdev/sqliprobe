import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def item_body(self, item):
        if "'" in item or '"' in item:
            return "You have an error in your SQL syntax near ''1''' (mysql)", 200
        if "1'='2" in item or "1=2" in item:
            return "no rows", 200
        return "<h1>item 1</h1><p>price 100</p>" * 20, 200

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/":
            body = ('<a href="/item?id=1">item</a>'
                    '<a href="/news/5">news</a>'
                    '<form method="post" action="/login">'
                    '<input name="user" value="admin"><input name="pass" value="1">'
                    "</form>")
            self.send_response(200)
        elif parsed.path.startswith("/news/"):
            seg = parsed.path.rsplit("/", 1)[-1]
            body, code = self.item_body(seg)
            self.send_response(code)
        else:
            q = parse_qs(parsed.query)
            item = q.get("id", ["1"])[0]
            body, code = self.item_body(item)
            if ("SLEEP" in item or "sleep" in item) and ("'" in item or '"' in item):
                time.sleep(6)
            self.send_response(code)
        data = body.encode()
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length).decode()
        q = parse_qs(raw)
        user = q.get("user", ["admin"])[0]
        body, code = self.item_body(user)
        self.send_response(code)
        data = body.encode()
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


HTTPServer(("127.0.0.1", 8765), H).serve_forever()
