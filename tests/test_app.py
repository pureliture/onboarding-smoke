import json
import pathlib
import sys
import threading
import unittest
import urllib.request
from http.server import ThreadingHTTPServer

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import Handler


class SmokeTest(unittest.TestCase):
    def test_health_handler_exists(self):
        self.assertTrue(callable(Handler.do_GET))

    def test_smoke_handler_exists(self):
        self.assertTrue(callable(Handler.do_POST))

    def test_dockerfile_pins_python(self):
        text = (ROOT / "Dockerfile").read_text(encoding="utf-8")
        self.assertIn("python:3.13-alpine", text)

    def test_http_endpoints(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f"http://127.0.0.1:{server.server_port}"

        with urllib.request.urlopen(f"{base}/healthz", timeout=5) as resp:
            self.assertEqual(resp.status, 200)
            health = json.loads(resp.read().decode("utf-8"))
        self.assertEqual(health, {"status": "ok", "app": "onboarding-smoke", "appVersion": "0.2.0"})

        with urllib.request.urlopen(f"{base}/smoke", timeout=5) as resp:
            self.assertEqual(resp.status, 200)
            smoke_get = json.loads(resp.read().decode("utf-8"))
        self.assertEqual(smoke_get, {"ok": True, "mode": "isolated"})

        req = urllib.request.Request(
            f"{base}/smoke",
            data=json.dumps({"probe": "canary"}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            self.assertEqual(resp.status, 200)
            smoke_post = json.loads(resp.read().decode("utf-8"))
        self.assertEqual(smoke_post, {"ok": True, "mode": "isolated", "probe": "canary"})


if __name__ == "__main__":
    unittest.main()
