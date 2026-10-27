import contextlib
import io
import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path

from tests._helpers import FIXTURES
import build_load_page
import build_report
import score
import validate_findings
from lib import paths


class EndToEndTest(unittest.TestCase):
    def test_full_pipeline_on_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            audit = Path(tmp) / "example-com"
            shutil.copytree(FIXTURES / "audit", audit)
            self.assertFalse(any(validate_findings.validate_dir(audit / "findings").values()))

            fdir = audit / "findings"
            findings = {a: json.loads((fdir / f"{a}.json").read_text()) for a in ["ux", "a11y", "visual", "tech", "seo"]}
            scores = score.compute_scores(findings, None, paths.config("scoring"), paths.config("rubric"))
            (fdir / "scores.json").write_text(json.dumps(scores))

            with contextlib.redirect_stdout(io.StringIO()):
                self.assertIsNone(build_load_page.build_load_page(audit))  # option off in fixture
                out = build_report.build_report(audit)
            html = out.read_text(encoding="utf-8")

            report = audit / "report"
            for ref in re.findall(r'(?:src|href)="(?!https?:|#|mailto:)([^"]+)"', html):
                self.assertTrue((report / ref).exists(), ref)
            n = len(json.loads((fdir / "top10.json").read_text())["items"])
            self.assertIn(f"Top {n}", html)
            for section_id in ["tu-sitio", "resultado", "top", "critica", "competencia", "extra", "plan"]:
                self.assertIn(f'id="{section_id}"', html)
            self.assertIn(f"{scores['overall']}<small>/100</small>", html)


if __name__ == "__main__":
    unittest.main()
