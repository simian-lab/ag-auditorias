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
        self.assertIn(">Puesto 12<", sec.html)
        self.assertIn(">No sales<", sec.html)

    def test_search_row_with_only_own_profiles(self):
        def f(doc):
            t = next(t for t in doc["search_tests"] if not t["appears"])
            t["who_appears"] = ["Instagram: Acme Box (@acmebox_)", "Latin Pack"]
        self._edit("seo.json", f)
        sec = extra.build(self.ctx(extra=True))
        self.assertIn(">Solo tu Instagram · puesto 1<", sec.html)

    def test_score_card_lists_unmet_seo_criteria(self):
        sec = extra.build(self.ctx(extra=True))
        self.assertIn('class="sa-extra-crit"', sec.html)
        self.assertIn("criterios cumplidos", sec.html)

    def test_search_row_without_position_keeps_plain_label(self):
        sec = extra.build(self.ctx(extra=True))
        self.assertIn(">Sí sales<", sec.html)

    def test_brand_queries_get_their_own_table(self):
        self._edit("seo.json", lambda d: d["search_tests"][1].__setitem__("query", "acmebox"))
        sec = extra.build(self.ctx(extra=True))
        self.assertIn("Cuando te buscan por tu nombre", sec.html)
        self.assertIn("Te encuentran en 0 de 1 búsquedas de compradores", sec.html)

    def test_whatsapp_today_uses_preview_title_when_given(self):
        self._edit("presence.json", lambda d: d["share_preview"].__setitem__("today_title", "Solo Shell"))
        sec = extra.build(self.ctx(extra=True))
        wa = sec.html[sec.html.index("Así se ve tu enlace en WhatsApp"):]
        self.assertIn("Solo Shell", wa)
        self.assertNotIn("Example – Inicio", wa)

    def test_whatsapp_today_shows_real_og_preview(self):
        def f(d):
            d["share_preview"]["today"] = {"home": {"og:title": "Example Hoy", "og:description": "Desc real de hoy"}}
            d["share_preview"]["today_og_image_local"] = "og-today.jpg"
        self._edit("presence.json", f)
        shutil.copy(self.audit / "screenshots" / "desktop-fullpage.jpg", self.audit / "screenshots" / "og-today.jpg")
        sec = extra.build(self.ctx(extra=True))
        wa = sec.html[sec.html.index("Así se ve tu enlace en WhatsApp"):sec.html.index("Propuesta", sec.html.index("Así se ve tu enlace en WhatsApp"))]
        self.assertIn("Desc real de hoy", wa)
        self.assertIn("og-today.jpg", wa)

    def test_whatsapp_today_shows_site_icon_without_og_image(self):
        self._edit("presence.json", lambda d: d["share_preview"].__setitem__("today_icon_local", "og-today-icon.png"))
        shutil.copy(self.audit / "screenshots" / "desktop-fullpage.jpg", self.audit / "screenshots" / "og-today-icon.png")
        sec = extra.build(self.ctx(extra=True))
        wa = sec.html[sec.html.index("Así se ve tu enlace en WhatsApp"):sec.html.index("Propuesta", sec.html.index("Así se ve tu enlace en WhatsApp"))]
        self.assertIn("sa-extra-mini", wa)
        self.assertIn("og-today-icon.png", wa)

    def test_whatsapp_today_icon_stays_small_with_og_description(self):
        def f(d):
            d["share_preview"]["today"] = {"home": {"og:title": "Example Hoy", "og:description": "Desc real de hoy"}}
            d["share_preview"]["today_og_image_local"] = "og-today-icon.png"  # agent mislabels the icon
        self._edit("presence.json", f)
        shutil.copy(self.audit / "screenshots" / "desktop-fullpage.jpg", self.audit / "screenshots" / "og-today-icon.png")
        sec = extra.build(self.ctx(extra=True))
        wa = sec.html[sec.html.index("Así se ve tu enlace en WhatsApp"):sec.html.index("Propuesta", sec.html.index("Así se ve tu enlace en WhatsApp"))]
        self.assertIn("sa-extra-mini", wa)
        self.assertNotIn("sa-extra-og", wa)
        self.assertIn("Desc real de hoy", wa)

    def test_serp_site_name_only_when_given(self):
        self.assertNotIn('class="sa-extra-site"', extra.build(self.ctx(extra=True)).html)
        self._edit("presence.json", lambda d: d["serp"]["today"][0].__setitem__("site_name", "example.com"))
        self.assertIn('class="sa-extra-site"', extra.build(self.ctx(extra=True)).html)

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
