import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tests._helpers import FIXTURES
import build_report
from report.sections import extra


class ExtraTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.audit = Path(self.tmp.name) / "example-com"
        shutil.copytree(FIXTURES / "audit", self.audit)

    def tearDown(self):
        self.tmp.cleanup()

    def ctx(self, **opts):
        meta = self.audit / "findings" / "meta.json"
        m = json.loads(meta.read_text())
        m["options"].update(opts)
        meta.write_text(json.dumps(m))
        return build_report.load_ctx(self.audit)

    def test_extra_omitted_when_option_off(self):
        self.assertIsNone(extra.build(self.ctx(extra=False)))

    def test_extra_renders_search_tests_and_previews(self):
        sec = extra.build(self.ctx(extra=True))
        self.assertIn("cajas de cartón para flores", sec.html)
        self.assertIn("Cajas de cartón en Mosquera | Example", sec.html)
        self.assertIn("1 de 2", sec.html)

    def test_nap_hidden_when_no_inconsistencies(self):
        p = self.audit / "findings" / "presence.json"
        doc = json.loads(p.read_text())
        doc["nap"]["inconsistencies"] = []
        p.write_text(json.dumps(doc))
        sec = extra.build(self.ctx(extra=True))
        self.assertNotIn("no dice lo mismo", sec.html)

    def test_ai_block_hidden_without_file(self):
        (self.audit / "findings" / "ai-visibility.json").unlink()
        sec = extra.build(self.ctx(extra=True))
        self.assertNotIn("Le preguntamos a la IA", sec.html)

    def test_brand_highlight_matches_variant(self):
        sec = extra.build(self.ctx(extra=True))
        self.assertIn('class="sa-extra-me">Acme Box S.A.S.', sec.html)
        self.assertNotIn('class="sa-extra-me">Latin Pack', sec.html)

    def test_share_image_only_when_local_file_exists(self):
        sec = extra.build(self.ctx(extra=True))
        self.assertNotIn("og-source.jpg", sec.html)
        shutil.copy(self.audit / "screenshots" / "desktop-fullpage.jpg", self.audit / "screenshots" / "og-source.jpg")
        sec = extra.build(self.ctx(extra=True))
        self.assertIn("assets/og-source.jpg", sec.html)


if __name__ == "__main__":
    unittest.main()
