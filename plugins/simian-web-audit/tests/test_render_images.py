import unittest

import tests._helpers  # noqa: F401  (puts scripts/ on sys.path)

from report import render


class ImagesTest(unittest.TestCase):
    def test_first_image_eager_rest_lazy_and_retry_script(self):
        sec = render.Section("a", None, '<img src="a.png"><p>x</p><img src="b.png"><img src="c.png">', "")
        html = render.page([sec], "t")
        self.assertIn('<img src="a.png">', html)
        self.assertIn('<img loading="lazy" src="b.png">', html)
        self.assertIn('<img loading="lazy" src="c.png">', html)
        self.assertIn(render.IMG_RETRY_JS, html.split("</head>")[0])

    def test_load_page_template_has_same_retry_script(self):
        from build_load_page import TEMPLATE
        self.assertIn(render.IMG_RETRY_JS.strip(), TEMPLATE.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
