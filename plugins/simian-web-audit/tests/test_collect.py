import base64
import json
import tempfile
import unittest
from pathlib import Path

from tests._helpers import PLUGIN  # noqa: F401
import collect_evidence

# 1x1 WebP
WEBP = base64.b64decode("UklGRiQAAABXRUJQVlA4IBgAAAAwAQCdASoBAAEAAwA0JaQAA3AA/vuUAAA=")


class FakeRun:
    def __init__(self):
        self.calls = []

    def __call__(self, argv, **kw):
        self.calls.append([str(a) for a in argv])
        # emulate tools writing their outputs
        for i, a in enumerate(argv):
            a = str(a)
            if a.startswith("--output-path="):
                Path(a.split("=", 1)[1]).write_text(json.dumps(_lh()), encoding="utf-8")
            if a.startswith("--screenshot="):
                Path(a.split("=", 1)[1]).write_bytes(b"png")
            if a == "--out":
                Path(argv[i + 1]).write_bytes(b"jpg")

        class R:
            returncode = 0
            stdout = ""
            stderr = ""
        return R()


def _lh():
    data = "data:image/webp;base64," + base64.b64encode(WEBP).decode()
    return {
        "categories": {"performance": {"score": 0.59}, "accessibility": {"score": 0.93}},
        "audits": {
            "largest-contentful-paint": {"numericValue": 8100},
            "total-byte-weight": {"numericValue": 13714 * 1024},
            "final-screenshot": {"details": {"data": data}},
        },
        "fullPageScreenshot": {"screenshot": {"data": data, "width": 412, "height": 3000}},
    }


class CollectTest(unittest.TestCase):
    def test_extract_writes_jpeg(self):
        run = FakeRun()
        with tempfile.TemporaryDirectory() as tmp:
            lh = Path(tmp) / "lh.json"
            lh.write_text(json.dumps(_lh()), encoding="utf-8")
            out = collect_evidence.extract_lighthouse_screenshots(lh, Path(tmp), "mobile", run=run)
            self.assertEqual([p.name for p in out], ["mobile-fullpage.jpg"])
            self.assertTrue(any("-s" in c and "jpeg" in c for c in run.calls), run.calls)
            self.assertTrue((Path(tmp) / "mobile-fullpage.webp").exists())

    def test_collect_builds_expected_commands(self):
        run = FakeRun()
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            for sub in ["raw", "screenshots"]:
                (d / sub).mkdir()
            summary = collect_evidence.collect(d, "https://example.com", run=run, fetch=lambda url: "<html></html>")
            lh_calls = [c for c in run.calls if c[0] == "lighthouse"]
            self.assertEqual(len(lh_calls), 2)
            self.assertTrue(any("--preset=desktop" in c for c in lh_calls))
            chrome = [c for c in run.calls if "Google Chrome" in c[0]]
            self.assertEqual(len(chrome), 1)
            self.assertIn("--window-size=1440,900", chrome[0])
            self.assertEqual((d / "raw" / "home.html").read_text(), "<html></html>")
            self.assertEqual(summary["mobile"]["total"], "13,4 MB")
            self.assertEqual(summary["mobile"]["lcp"], "8,1 s")

    def test_collect_never_shoots_narrow_chrome(self):
        run = FakeRun()
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            for sub in ["raw", "screenshots"]:
                (d / sub).mkdir()
            collect_evidence.collect(d, "https://example.com", run=run, fetch=lambda url: "")
            for c in run.calls:
                for a in c:
                    if a.startswith("--window-size="):
                        self.assertGreaterEqual(int(a.split("=")[1].split(",")[0]), 500)


class UrlFromMetaTest(unittest.TestCase):
    def test_url_defaults_to_meta(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "findings").mkdir()
            (d / "findings" / "meta.json").write_text('{"url": "https://example.com"}', encoding="utf-8")
            self.assertEqual(collect_evidence.resolve_url(d, None), "https://example.com")
            self.assertEqual(collect_evidence.resolve_url(d, "https://other.co"), "https://other.co")


if __name__ == "__main__":
    unittest.main()
