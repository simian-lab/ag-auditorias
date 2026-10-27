import contextlib
import io
import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path

from tests._helpers import FIXTURES
import build_report
from report import render


class RenderCoreTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.audit = Path(self.tmp.name) / "example-com"
        shutil.copytree(FIXTURES / "audit", self.audit)

    def tearDown(self):
        self.tmp.cleanup()

    def build(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            out = build_report.build_report(self.audit)
        return out.read_text(encoding="utf-8"), buf.getvalue()

    def set_items(self, n):
        p = self.audit / "findings" / "top10.json"
        doc = json.loads(p.read_text(encoding="utf-8"))
        doc["items"] = doc["items"][:n]
        p.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")

    def test_title_uses_top_n(self):
        html, out = self.build()
        self.assertIn("Top 7", html)
        self.assertNotIn("Top 10", html)
        self.assertNotIn("warning", out.lower())

    def test_warns_when_fewer_than_min(self):
        self.set_items(4)
        html, out = self.build()
        self.assertIn("Top 4", html)
        self.assertIn("warning", out.lower())

    def test_escapes_text(self):
        html, _ = self.build()
        self.assertIn("&amp; &lt;b&gt;John&lt;/b&gt;", html)
        self.assertNotIn("<b>John</b>", html)

    def test_item_without_shot_or_missing_image_renders(self):
        html, _ = self.build()
        self.assertIn("Tu sitio no está pidiendo la venta", html)  # shot: null
        self.assertIn("Tus botones verdes casi no se leen", html)  # missing.jpg
        self.assertNotIn("missing.jpg", html)

    def test_no_external_resources(self):
        html, _ = self.build()
        self.assertFalse(re.findall(r'src="https?://', html))
        self.assertFalse(re.findall(r"url\(['\"]?https?://", html))

    def test_no_cta(self):
        html, _ = self.build()
        self.assertNotIn("wa.me", html)
        self.assertNotIn("mailto:", html)

    def test_assets_copied_and_resolvable(self):
        html, _ = self.build()
        report = self.audit / "report"
        for ref in re.findall(r'(?:src|href)="(assets/[^"#?]+)"', html):
            self.assertTrue((report / ref).exists(), ref)
        self.assertTrue((report / "assets" / "fonts" / "Vollkorn-latin-wght.woff2").exists())

    def test_score_shows_criteria_counts_and_list(self):
        import score as score_mod
        from lib import paths
        f = self.audit / "findings"
        findings = {a: json.loads((f / f"{a}.json").read_text()) for a in ["ux", "a11y", "visual", "tech"]}
        s = score_mod.compute_scores(findings, None, paths.config("scoring"), paths.config("rubric"))
        (f / "scores.json").write_text(json.dumps(s))
        html, _ = self.build()
        self.assertIn("8 de 11 criterios", html)  # ux fixture: 3 fails
        self.assertNotIn("parcial", html.split("Ver los criterios evaluados")[0])
        self.assertIn("Hay un botón visible para cotizar o contactar ventas", html)
        self.assertIn("Ver los criterios evaluados", html)

    def test_partial_criteria_shown(self):
        import score as score_mod
        from lib import paths
        f = self.audit / "findings"
        ux = json.loads((f / "ux.json").read_text())
        ux["checks"][1]["result"] = "partial"
        (f / "ux.json").write_text(json.dumps(ux, ensure_ascii=False))
        findings = {a: json.loads((f / f"{a}.json").read_text()) for a in ["ux", "a11y", "visual", "tech"]}
        (f / "scores.json").write_text(json.dumps(score_mod.compute_scores(findings, None, paths.config("scoring"), paths.config("rubric"))))
        html, _ = self.build()
        self.assertIn("8 de 11 criterios · 1 parcial", html)
        self.assertIn("sa-score-pa", html)

    def test_classes_prefixed(self):
        ctx = build_report.load_ctx(self.audit)
        for mod in build_report.SECTIONS:
            sec = mod.build(ctx)
            if sec is None:
                continue
            for attr in re.findall(r'class="([^"]*)"', sec.html):
                for token in attr.split():
                    if "${" in token:
                        continue
                    self.assertTrue(token.startswith("sa-") or token in render.BASE_CLASSES,
                                    f"{mod.__name__}: {token}")


if __name__ == "__main__":
    unittest.main()
