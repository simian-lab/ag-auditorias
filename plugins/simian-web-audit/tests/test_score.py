import unittest

from tests._helpers import PLUGIN  # noqa: F401
from lib import paths
import score

CFG = paths.config("scoring")
RUBRIC = {"version": "1", "areas": {
    "ux": [{"id": "a", "weight": 3}, {"id": "b", "weight": 1}, {"id": "c", "weight": 2}],
    "a11y": [{"id": "d", "weight": 1}, {"id": "e", "weight": 1}],
    "visual": [{"id": "f", "weight": 1}],
    "tech": [{"id": "g", "weight": 2}, {"id": "h", "weight": 2}],
    "seo": [{"id": "i", "weight": 1}, {"id": "j", "weight": 1}],
}}


def checks(**results):
    return {"findings": [], "checks": [{"id": k, "result": v, "evidence": "x"} for k, v in results.items()]}


ALL = {"ux": checks(a="pass", b="pass", c="pass"), "a11y": checks(d="pass", e="pass"),
       "visual": checks(f="pass"), "tech": checks(g="pass", h="pass")}


class ScoreTest(unittest.TestCase):
    def test_shipped_config_uses_rubric(self):
        self.assertEqual((CFG["version"], CFG["method"]), ("3", "rubric"))

    def test_area_is_weighted_share_of_passed_criteria(self):
        s = score.compute_scores({**ALL, "ux": checks(a="pass", b="fail", c="fail")}, None, CFG, RUBRIC)
        self.assertEqual(s["ux"], 50)  # 3 of 6 weight
        self.assertEqual(s["detail"]["ux"], {"passed": 1, "partial": 0, "total": 3})

    def test_not_applicable_criteria_are_excluded(self):
        s = score.compute_scores({**ALL, "ux": checks(a="fail", b="pass", c="na")}, None, CFG, RUBRIC)
        self.assertEqual(s["ux"], 25)  # 1 of 4 weight
        self.assertEqual(s["detail"]["ux"], {"passed": 1, "partial": 0, "total": 2})

    def test_partial_counts_half_weight(self):
        s = score.compute_scores({**ALL, "ux": checks(a="partial", b="fail", c="partial")}, None, CFG, RUBRIC)
        self.assertEqual(s["ux"], 42)  # (1.5 + 1) / 6
        self.assertEqual(s["detail"]["ux"], {"passed": 0, "partial": 2, "total": 3})

    def test_tech_blends_with_lighthouse(self):
        lh = {"categories": {"performance": {"score": 0.59}, "best-practices": {"score": 1.0}}}
        s = score.compute_scores({**ALL, "tech": checks(g="pass", h="fail")}, lh, CFG, RUBRIC)
        self.assertEqual(s["tech"], 65)  # round((50 + 79.5) / 2)

    def test_overall_mean_of_base_areas_and_seo_separate(self):
        s = score.compute_scores({**ALL, "ux": checks(a="fail", b="fail", c="fail"), "seo": checks(i="pass", j="fail")},
                                 None, CFG, RUBRIC)
        self.assertEqual(s["overall"], 75)  # 0, 100, 100, 100
        self.assertEqual(s["seo"], 50)
        self.assertEqual(s["rubric_version"], "1")

    def test_missing_checks_raise(self):
        with self.assertRaises(ValueError):
            score.compute_scores({**ALL, "ux": {"findings": []}}, None, CFG, RUBRIC)

    def test_missing_area_raises(self):
        with self.assertRaises(ValueError):
            score.compute_scores({"ux": ALL["ux"]}, None, CFG, RUBRIC)


if __name__ == "__main__":
    unittest.main()
