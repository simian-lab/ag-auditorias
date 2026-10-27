import json
import tempfile
import unittest
from pathlib import Path

from tests._helpers import PLUGIN
import init_audit


class SlugTest(unittest.TestCase):
    def test_slug_strips_www_scheme_and_path(self):
        self.assertEqual(init_audit.slugify("https://www.acmebox.com/"), "acmebox-com")

    def test_slug_lowercases_and_drops_query(self):
        self.assertEqual(init_audit.slugify("HTTP://Example.co/a/b?x=1"), "example-co")

    def test_slug_keeps_hyphens(self):
        self.assertEqual(init_audit.slugify("https://www.Acme-Box.com/inicio/"), "acme-box-com")

    def test_slug_without_scheme(self):
        self.assertEqual(init_audit.slugify("acmebox.com"), "acmebox-com")


class InitAuditTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_creates_folders_and_brief(self):
        d = init_audit.init_audit("https://www.acmebox.com/", {"business": "Cajas de cartón"}, base=self.base)
        self.assertEqual(d, self.base / "audits" / "acmebox-com")
        for sub in ["raw", "screenshots", "findings", "report/assets"]:
            self.assertTrue((d / sub).is_dir(), sub)
        brief = (d / "BRIEF.md").read_text(encoding="utf-8")
        self.assertIn("acmebox.com", brief)
        self.assertIn("Cajas de cartón", brief)
        self.assertNotIn("{{", brief)

    def test_rerun_keeps_findings(self):
        d = init_audit.init_audit("https://acmebox.com", {}, base=self.base)
        (d / "findings" / "ux.json").write_text('{"keep": true}', encoding="utf-8")
        created = json.loads((d / "findings" / "meta.json").read_text())["created_at"]
        init_audit.init_audit("https://www.acmebox.com/x", {}, base=self.base)
        self.assertEqual((d / "findings" / "ux.json").read_text(), '{"keep": true}')
        self.assertEqual(json.loads((d / "findings" / "meta.json").read_text())["created_at"], created)

    def test_meta_records_versions(self):
        d = init_audit.init_audit("https://acmebox.com", {}, base=self.base, options={"extra": True})
        meta = json.loads((d / "findings" / "meta.json").read_text())
        plugin_version = json.loads((PLUGIN / ".claude-plugin" / "plugin.json").read_text())["version"]
        scoring_version = json.loads((PLUGIN / "config" / "scoring.json").read_text())["version"]
        self.assertEqual(meta["plugin_version"], plugin_version)
        self.assertEqual(meta["scoring_version"], scoring_version)
        self.assertEqual(meta["domain"], "acmebox.com")
        self.assertEqual(meta["options"], {"extra": True})


if __name__ == "__main__":
    unittest.main()
