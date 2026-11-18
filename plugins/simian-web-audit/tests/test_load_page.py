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
import measure_load

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

    def test_load_caveat_from_benchmark_is_shown_escaped(self):
        bench = self.audit / "findings" / "benchmark.json"
        b = json.loads(bench.read_text())
        b["load_caveat_es"] = "Ojo: una animación <tapa> la portada."
        bench.write_text(json.dumps(b))
        html = self.run_build().read_text(encoding="utf-8")
        self.assertIn("Ojo: una animación &lt;tapa&gt; la portada.", html)

    def test_no_caveat_paragraph_without_field(self):
        html = self.run_build().read_text(encoding="utf-8")
        self.assertNotIn('class="caveat"', html)

    def test_page_kept_but_not_linked_when_client_is_faster(self):
        (self.audit / "raw" / "lighthouse-mobile.json").write_text(json.dumps(lh(300, 600, [500, 1000])), encoding="utf-8")
        self.assertTrue(self.run_build().exists())
        self.assertFalse(build_load_page.show_in_report(self.audit))
        with contextlib.redirect_stdout(io.StringIO()):
            html = build_report.build_report(self.audit).read_text(encoding="utf-8")
        self.assertNotIn("feature-carga.html", html)

    def test_script_injection_is_escaped(self):
        bench = self.audit / "findings" / "benchmark.json"
        b = json.loads(bench.read_text())
        b["competitors"][0]["name"] = "</script><b>x"
        bench.write_text(json.dumps(b))
        html = self.run_build().read_text(encoding="utf-8")
        self.assertNotIn("</script><b>x", html)


class MeasureTest(unittest.TestCase):
    setUp, tearDown, set_option, run_build = LoadPageTest.setUp, LoadPageTest.tearDown, LoadPageTest.set_option, LoadPageTest.run_build

    def fake_run(self, lcps):
        calls = []

        def run(cmd, **_):
            url, out = cmd[1], Path(cmd[-1].split("=", 1)[1])
            calls.append(url)
            out.write_text(json.dumps(lh(100, lcps[url].pop(0), [500, 1000])), encoding="utf-8")
        return run, calls

    def test_same_step_rounds_keep_median_and_drive_the_page(self):
        b = json.loads((self.audit / "findings" / "benchmark.json").read_text())
        comp = b["competitors"][0]["url"]
        run, calls = self.fake_run({"https://example.com": [900, 5000, 700], comp: [3000, 2000, 2500]})
        with contextlib.redirect_stdout(io.StringIO()):
            summary = measure_load.measure(self.audit, 3, run=run)
        self.assertEqual(calls[:2], ["https://example.com", comp])  # rotates order each round
        self.assertEqual(calls[2:4], [comp, "https://example.com"])
        self.assertEqual(summary["client"]["median_ms"], 900)
        self.assertEqual(summary["uno"]["median_ms"], 2500)
        self.assertFalse((self.audit / "raw" / "load-tmp").exists())
        # client 900 ms vs competitor 2500 ms -> page built but not linked
        self.run_build()
        self.assertFalse(build_load_page.show_in_report(self.audit))


class CopyTest(unittest.TestCase):
    def site(self, me, fcp, lcp):
        return {"me": me, "fcp": fcp, "lcp": lcp}

    def test_claims_competition_ahead_only_when_client_slower_on_both(self):
        h, _ = build_load_page._copy("x.com", [self.site(True, 3000, 8000), self.site(False, 1000, 2000)])
        self.assertIn("tu competencia ya mostró su oferta", h)

    def test_client_slower_than_majority(self):
        s = lambda lcp, me=False: self.site(me, 0, lcp)  # noqa: E731
        self.assertTrue(build_load_page.client_loads_slower([s(5000, True), s(1000), s(2000), s(9000)]))
        # Metric's case: only one of three competitors is faster -> hide
        self.assertFalse(build_load_page.client_loads_slower([s(1658, True), s(1329), s(4879), s(9661)]))
        self.assertTrue(build_load_page.client_loads_slower([s(1000, True)]))

    def test_neutral_headline_when_client_paints_first(self):
        h, _ = build_load_page._copy("x.com", [self.site(True, 1300, 7700), self.site(False, 1500, 2000)])
        self.assertEqual(h, "Así carga tu sitio frente a tu competencia.")


if __name__ == "__main__":
    unittest.main()
