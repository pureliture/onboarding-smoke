import pathlib
import unittest

from app import Handler


class SmokeTest(unittest.TestCase):
    def test_health_handler_exists(self):
        self.assertTrue(callable(Handler.do_GET))

    def test_smoke_handler_exists(self):
        self.assertTrue(callable(Handler.do_POST))

    def test_dockerfile_pins_python(self):
        text = pathlib.Path("Dockerfile").read_text(encoding="utf-8")
        self.assertIn("python:3.13-alpine", text)


if __name__ == "__main__":
    unittest.main()
