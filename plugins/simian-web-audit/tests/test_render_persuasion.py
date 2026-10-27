import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path

from tests._helpers import FIXTURES
import build_report
from report.sections import benchmark, critique, plan, redesign, simian

CASES = [
    {"slug": "noticiero", "client": "90 Minutos", "headline": "WordPress lento", "url": "https://simian.co/n/", "image": "n.png", "results": ["Más rápido"], "matches": ["wordpress", "performance", "security"]},
    {"slug": "veyalthi", "client": "Veyalthi", "headline": "Agente por WhatsApp", "url": "https://simian.co/v/", "image": "v.jpg", "results": ["24/7"], "matches": ["whatsapp", "quote-cta"]},
    {"slug": "salud", "client": "Salud Total", "headline": "Portal accesible", "url": "https://simian.co/s/", "image": "s.png", "results": ["Accesible"], "matches": ["ux", "accessibility"]},
    {"slug": "otro", "client": "Otro", "headline": "Otro", "url": "https://simian.co/o/", "image": "o.png", "results": [], "matches": ["interactive"]},
]


class PersuasionTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.audit = Path(self.tmp.name) / "example-com"
        shutil.copytree(FIXTURES / "audit", self.audit)
        (self.audit / "report" / "assets").mkdir(parents=True, exist_ok=True)
        shutil.copy(self.audit / "screenshots" / "desktop-viewport.png", self.audit / "screenshots" / "bench-uno.png")
        shutil.copy(self.audit / "screenshots" / "desktop-viewport.png", self.audit / "screenshots" / "ui-crop-btn.png")

    def tearDown(self):
        self.tmp.cleanup()

    def ctx(self):
        return build_report.load_ctx(self.audit)

    def test_pick_cases_whatsapp_first(self):
        items = json.loads((self.audit / "findings" / "top10.json").read_text())["items"]
        picked = simian.pick_cases(CASES, items, k=3)
        self.assertEqual(picked[0][0]["slug"], "veyalthi")
        self.assertIn(1, picked[0][1])
        self.assertEqual(len(picked), 3)
        self.assertNotIn("otro", [c["slug"] for c, _ in picked])

    def test_benchmark_omitted_without_file(self):
        (self.audit / "findings" / "benchmark.json").unlink()
        self.assertIsNone(benchmark.build(self.ctx()))

    def test_benchmark_client_first_and_assets_exist(self):
        sec = benchmark.build(self.ctx())
        self.assertLess(sec.html.index("Tu sitio"), sec.html.index("Competidor Uno"))
        self.assertIn("13,4 MB", sec.html)

    def test_critique_skips_missing_crop(self):
        sec = critique.build(self.ctx())
        self.assertIn("ui-crop-btn.png", sec.html)
        self.assertNotIn("ui-crop-missing.png", sec.html)

    def test_redesign_omitted_without_screenshot(self):
        self.assertIsNone(redesign.build(self.ctx()))

    def test_redesign_present_with_screenshot(self):
        shutil.copy(self.audit / "screenshots" / "desktop-viewport.png", self.audit / "report" / "assets" / "redesign-desktop.png")
        sec = redesign.build(self.ctx())
        self.assertIn("redesign-desktop.png", sec.html)

    def test_plan_lists_every_item_once(self):
        sec = plan.build(self.ctx())
        for n in range(1, 8):
            self.assertEqual(len(re.findall(rf'data-n="{n}"', sec.html)), 2, n)

    def test_optional_stage_absent_without_extra(self):
        for f in ["seo.json", "presence.json"]:
            p = self.audit / "findings" / f
            if p.exists():
                p.unlink()
        sec = plan.build(self.ctx())
        self.assertNotIn("OPCIONAL", sec.html)

    def test_optional_stage_with_redesign(self):
        shutil.copy(self.audit / "screenshots" / "desktop-viewport.png", self.audit / "report" / "assets" / "redesign-desktop.png")
        sec = plan.build(self.ctx())
        self.assertIn("OPCIONAL", sec.html)
        self.assertIn("Rediseño de la portada", sec.html)

    def test_simian_section_uses_cases(self):
        ctx = self.ctx()
        ctx["cases"] = CASES
        sec = simian.build(ctx)
        self.assertIn("Veyalthi", sec.html)
        self.assertIsNone(simian.build({**ctx, "cases": []}))

    def test_simian_section_hidden_for_internal_audits(self):
        ctx = self.ctx()
        ctx["cases"] = CASES
        ctx["meta"] = {"options": {"internal": True}}
        self.assertIsNone(simian.build(ctx))


if __name__ == "__main__":
    unittest.main()
