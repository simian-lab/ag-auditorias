import base64
import contextlib
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tests._helpers import FIXTURES
import build_load_page
import build_report

JPEG = base64.b64encode(b"\xff\xd8\xff\xe0fakejpeg").decode()


def lh(fcp_obs, lcp_obs, timings):
    return {
        "audits": {
            "screenshot-thumbnails": {"details": {"items": [{"timing": t, "data": f"data:image/jpeg;base64,{JPEG}"} for t in timings]}},
            "metrics": {"details": {"items": [{"observedFirstContentfulPaint": fcp_obs, "observedLargestContentfulPaint": lcp_obs}]}},
            "first-contentful-paint": {"numericValue": fcp_obs * 1.4},
            "largest-contentful-paint": {"numericValue": lcp_obs * 2.8},
            "speed-index": {"numericValue": lcp_obs * 1.1},
        }
    }


class LoadPageTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.audit = Path(self.tmp.name) / "example-com"
        shutil.copytree(FIXTURES / "audit", self.audit)
        raw = self.audit / "raw"
        raw.mkdir(exist_ok=True)
        (raw / "lighthouse-mobile.json").write_text(json.dumps(lh(2300, 23100, [3000, 1000, 2000])), encoding="utf-8")
        (raw / "bench-uno-lh.json").write_text(json.dumps(lh(400, 900, [500, 1000])), encoding="utf-8")
        self.set_option(True)

    def tearDown(self):
        self.tmp.cleanup()

    def set_option(self, value):
        meta = self.audit / "findings" / "meta.json"
        m = json.loads(meta.read_text())
        m["options"]["load_page"] = value
        meta.write_text(json.dumps(m))

    def run_build(self):
        with contextlib.redirect_stdout(io.StringIO()):
            return build_load_page.build_load_page(self.audit)

    def test_extract_frames_in_timing_order(self):
        frames = build_load_page.extract_frames(lh(1, 2, [3000, 1000, 2000]))
        self.assertEqual([f[0] for f in frames], [1000, 2000, 3000])
        self.assertEqual(frames[0][2], "jpg")

    def test_page_built_with_sites_and_no_placeholders(self):
        out = self.run_build()
        html = out.read_text(encoding="utf-8")
        self.assertNotIn("{{", html)
        self.assertIn('"name": "Competidor Uno"', html)
        self.assertIn('"me": true', html)
        self.assertTrue((self.audit / "report" / "assets" / "film" / "client-1000.jpg").exists())
        self.assertTrue((self.audit / "report" / "assets" / "film" / "uno-500.jpg").exists())
        self.assertTrue((self.audit / "report" / "assets" / "desktop-viewport.png").exists())
        self.assertNotIn("googleapis", html)

    def test_frames_before_first_paint_marked_blank(self):
        sites = build_load_page.site_data(lh(2300, 23100, [1000, 3000]), "client", "Tu sitio", "example.com", True)
        self.assertEqual(sites["frames"], [[1000, 1], [3000]])

    def test_timeline_end_gives_whole_second_ticks(self):
        for lcp in [900, 5700, 23100, 65000]:
            end = build_load_page.timeline_end([lcp])
            self.assertEqual(end % 6000, 0, lcp)
            self.assertGreaterEqual(end, lcp)

    def test_not_built_when_option_off(self):
        self.set_option(False)
        self.assertIsNone(self.run_build())
        self.assertFalse((self.audit / "report" / "feature-carga.html").exists())

    def test_teaser_follows_page_presence(self):
        with contextlib.redirect_stdout(io.StringIO()):
            html = build_report.build_report(self.audit).read_text(encoding="utf-8")
        self.assertNotIn("feature-carga.html", html)
        self.run_build()
        with contextlib.redirect_stdout(io.StringIO()):
            html = build_report.build_report(self.audit).read_text(encoding="utf-8")
        self.assertIn('href="feature-carga.html"', html)

    def test_script_injection_is_escaped(self):
        bench = self.audit / "findings" / "benchmark.json"
        b = json.loads(bench.read_text())
        b["competitors"][0]["name"] = "</script><b>x"
        bench.write_text(json.dumps(b))
        html = self.run_build().read_text(encoding="utf-8")
        self.assertNotIn("</script><b>x", html)


if __name__ == "__main__":
    unittest.main()
