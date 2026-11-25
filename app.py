import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MODE = os.environ.get("APP_MODE", "isolated")
APP_VERSION = os.environ.get("APP_VERSION", "0.2.0")


class Handler(BaseHTTPRequestHandler):
    def _json(self, status, payload):
        body = json.dumps(payload).encode() + b"\n"
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/healthz":
            return self._json(200, {"status": "ok", "app": "onboarding-smoke", "appVersion": APP_VERSION})
        if self.path == "/smoke":
            return self._json(200, {"ok": True, "mode": MODE})
        return self._json(404, {"error": "not_found"})

    def do_POST(self):
        if self.path != "/smoke":
            return self._json(404, {"error": "not_found"})
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length) or b"{}")
        return self._json(200, {"ok": True, "mode": MODE, "probe": payload.get("probe")})

    def log_message(self, *_args):
        return


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", int(os.environ.get("PORT", "8080"))), Handler).serve_forever()
