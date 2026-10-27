import unittest

from tests._helpers import FIXTURES
import refresh_simian_cases

HTML = (FIXTURES / "portfolio" / "portafolio.html").read_text(encoding="utf-8")


class RefreshCasesTest(unittest.TestCase):
    def test_parse_portfolio_finds_five_cases_in_order(self):
        cases = refresh_simian_cases.parse_portfolio(HTML, existing=[])
        self.assertEqual([c["slug"] for c in cases],
                         ["veyalthi", "elecciones-el-tiempo", "salud-total", "app-externado", "noticiero-90-minutos"])
        v = cases[0]
        self.assertEqual(v["client"], "Veyalthi")
        self.assertEqual(v["image_url"], "https://simian.co/assets/img/proyectos/veyalthi/card-veyalthi.jpg")
        self.assertEqual(v["image"], "card-veyalthi.jpg")
        self.assertEqual(v["url"], "https://simian.co/veyalthi/")

    def test_existing_curated_fields_are_preserved(self):
        existing = [{"slug": "veyalthi", "matches": ["whatsapp"], "results": ["24/7"], "headline": "Curated"}]
        v = refresh_simian_cases.parse_portfolio(HTML, existing=existing)[0]
        self.assertEqual(v["matches"], ["whatsapp"])
        self.assertEqual(v["results"], ["24/7"])
        self.assertEqual(v["headline"], "Curated")

    def test_new_case_gets_empty_curation(self):
        sal = refresh_simian_cases.parse_portfolio(HTML, existing=[])[2]
        self.assertEqual(sal["matches"], [])
        self.assertTrue(sal["headline"])


if __name__ == "__main__":
    unittest.main()
