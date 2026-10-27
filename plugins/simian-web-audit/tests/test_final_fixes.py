import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tests._helpers import FIXTURES, PLUGIN
import build_report
import refresh_simian_cases
import score
import validate_findings
from lib.validate import validate
from report.sections import extra, plan, redesign


def schema(name):
    return json.loads((PLUGIN / "schemas" / f"{name}.schema.json").read_text(encoding="utf-8"))


class FinalFixesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.audit = Path(self.tmp.name) / "example-com"
        shutil.copytree(FIXTURES / "audit", self.audit)
        (self.audit / "report" / "assets").mkdir(parents=True, exist_ok=True)
        self.f = self.audit / "findings"

    def tearDown(self):
        self.tmp.cleanup()

    def edit(self, name, fn):
        p = self.f / name
        doc = json.loads(p.read_text(encoding="utf-8"))
        fn(doc)
        p.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")

    # I-1: a missing area must not be scored as 100
    def test_missing_area_file_is_reported(self):
        (self.f / "ux.json").unlink()
        self.assertIn("ux.json", validate_findings.validate_dir(self.f))
        self.assertTrue(validate_findings.validate_dir(self.f)["ux.json"])
        self.assertEqual(score.missing_areas(self.f), ["ux"])

    # I-2: valid data must not crash the build
    def test_checks_row_needs_label_and_status(self):
        doc = json.loads((self.f / "top10.json").read_text())
        doc["items"][6]["checks"] = [["HSTS"]]
        self.assertTrue(validate(doc, schema("top10")))
        doc["items"][6]["checks"] = [["HSTS", "maybe"]]
        self.assertTrue(validate(doc, schema("top10")))

    def test_benchmark_client_shape_is_validated(self):
        doc = json.loads((self.f / "benchmark.json").read_text())
        del doc["client"]["five_second"]["quote_cta"]
        self.assertTrue(validate(doc, schema("benchmark")))

    def test_empty_serp_does_not_crash_extra(self):
        self.edit("presence.json", lambda d: d["serp"].update(today=[], proposed=[]))
        sec = extra.build(build_report.load_ctx(self.audit))
        self.assertNotIn("Así apareces en Google", sec.html)

    # I-3: redesign lists the Top items it solves
    def test_redesign_lists_solved_items(self):
        shutil.copy(self.audit / "screenshots" / "desktop-viewport.png", self.audit / "report" / "assets" / "redesign-desktop.png")
        (self.f / "redesign.json").write_text('{"solves": [3, 1]}', encoding="utf-8")
        html = redesign.build(build_report.load_ctx(self.audit)).html
        self.assertIn("#1", html)
        self.assertIn("No hay forma clara de pedir una cotización", html)

    # I-4: plan and extra agree on whether the Extra exists
    def test_plan_has_no_extra_rows_when_extra_off(self):
        self.edit("meta.json", lambda d: d["options"].update(extra=False))
        html = plan.build(build_report.load_ctx(self.audit)).html
        self.assertNotIn("E1", html)

    def test_presence_renders_without_seo(self):
        (self.f / "seo.json").unlink()
        ctx = build_report.load_ctx(self.audit)
        self.assertTrue(extra.enabled(ctx))
        sec = extra.build(ctx)
        self.assertIn("Así apareces en Google", sec.html)
        self.assertIn("E1", plan.build(ctx).html)

    # M-7: refresh must not wipe curated cases
    def test_refresh_aborts_when_nothing_parsed(self):
        with self.assertRaises(SystemExit):
            refresh_simian_cases.ensure_cases([])

    # M-11: no prospect names in the shared repo's tests and fixtures
    def test_fixtures_have_no_real_prospect_names(self):
        for f in list((PLUGIN / "tests").rglob("*.py")) + list((PLUGIN / "tests" / "fixtures" / "audit").rglob("*.json")):
            if f.name == "test_final_fixes.py":
                continue
            self.assertNotIn("biopacking", f.read_text(encoding="utf-8").lower(), f.name)


if __name__ == "__main__":
    unittest.main()
