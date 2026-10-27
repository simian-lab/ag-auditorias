import unittest

from tests._helpers import PLUGIN  # noqa: F401
import preflight


class PreflightTest(unittest.TestCase):
    def test_preflight_reports_missing_lighthouse(self):
        hints = preflight.check(which=lambda n: None if n == "lighthouse" else f"/usr/bin/{n}", exists=lambda p: True)
        self.assertEqual(len(hints), 1)
        self.assertIn("npm i -g lighthouse", hints[0])

    def test_preflight_ok_returns_empty(self):
        self.assertEqual(preflight.check(which=lambda n: f"/usr/bin/{n}", exists=lambda p: True), [])

    def test_preflight_reports_missing_chrome(self):
        hints = preflight.check(which=lambda n: f"/usr/bin/{n}", exists=lambda p: False)
        self.assertEqual(len(hints), 1)
        self.assertIn("Chrome", hints[0])


if __name__ == "__main__":
    unittest.main()
