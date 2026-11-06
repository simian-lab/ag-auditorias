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

    def _edit(self, name, fn):
        p = self.audit / "findings" / name
        doc = json.loads(p.read_text())
        fn(doc)
        p.write_text(json.dumps(doc))

    def test_search_row_shows_google_position(self):
        def f(doc):
            doc["search_tests"][1]["position_or_note"] = "Puesto 12 (segunda página): «Example»"
        self._edit("seo.json", f)
        sec = extra.build(self.ctx(extra=True))
        self.assertIn("Apareces · puesto 12", sec.html)
        self.assertIn(">No apareces<", sec.html)

    def test_search_row_without_position_keeps_plain_label(self):
        sec = extra.build(self.ctx(extra=True))
        self.assertIn(">Apareces<", sec.html)

    def test_whatsapp_today_uses_preview_title_when_given(self):
        self._edit("presence.json", lambda d: d["share_preview"].__setitem__("today_title", "Solo Shell"))
        sec = extra.build(self.ctx(extra=True))
        wa = sec.html[sec.html.index("Así se ve tu enlace en WhatsApp"):]
        self.assertIn("Solo Shell", wa)
        self.assertNotIn("Example – Inicio", wa)

    def test_whatsapp_today_falls_back_to_serp_title(self):
        sec = extra.build(self.ctx(extra=True))
        wa = sec.html[sec.html.index("Así se ve tu enlace en WhatsApp"):]
        self.assertIn("Example – Inicio", wa)

    def test_serp_shows_real_google_snippet_when_given(self):
        self._edit("presence.json", lambda d: d["serp"]["today"][0].__setitem__("google_snippet", "Fundada en 2006."))
        sec = extra.build(self.ctx(extra=True))
        self.assertIn("Fundada en 2006.", sec.html)
        self.assertIn("Google toma este texto de tu página", sec.html)
        self.assertNotIn("Google improvisa", sec.html)

    def test_serp_without_description_or_snippet_keeps_warning(self):
        sec = extra.build(self.ctx(extra=True))
        self.assertIn("Google improvisa", sec.html)

    def test_ai_engine_keys_render_with_brand_names(self):
        def f(doc):
            doc["answers"][0]["engine"] = "chatgpt"
        self._edit("ai-visibility.json", f)
        sec = extra.build(self.ctx(extra=True))
        self.assertIn("<span>ChatGPT</span>", sec.html)
        self.assertNotIn("<span>chatgpt</span>", sec.html)

    def test_share_image_only_when_local_file_exists(self):
        sec = extra.build(self.ctx(extra=True))
        self.assertNotIn("og-source.jpg", sec.html)
        shutil.copy(self.audit / "screenshots" / "desktop-fullpage.jpg", self.audit / "screenshots" / "og-source.jpg")
        sec = extra.build(self.ctx(extra=True))
        self.assertIn("assets/og-source.jpg", sec.html)


if __name__ == "__main__":
    unittest.main()
