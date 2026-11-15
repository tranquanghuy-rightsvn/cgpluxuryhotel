#!/usr/bin/env python3
"""Local receiver: saves DOM/style dumps POSTed from the browser into .work/dump/."""
import http.server, os, re, sys
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dump")
class H(http.server.BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Private-Network", "true")
    def do_OPTIONS(self):
        self.send_response(204); self._cors(); self.end_headers()
    def do_POST(self):
        name = re.sub(r"[^a-zA-Z0-9_.-]", "", self.path.strip("/")) or "dump"
        data = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        open(os.path.join(OUT, name), "wb").write(data)
        self.send_response(200); self._cors(); self.end_headers(); self.wfile.write(b"ok")
    def log_message(self, *a): pass
http.server.HTTPServer(("127.0.0.1", 8766), H).serve_forever()
