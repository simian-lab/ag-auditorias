import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tests._helpers import FIXTURES, PLUGIN
from lib.validate import validate
import validate_findings


def load(name):
    return json.loads((FIXTURES / "audit" / "findings" / name).read_text(encoding="utf-8"))


def schema(name):
    return json.loads((PLUGIN / "schemas" / f"{name}.schema.json").read_text(encoding="utf-8"))


class ValidateTest(unittest.TestCase):
    def test_valid_area_fixture_has_no_errors(self):
        self.assertEqual(validate(load("ux.json"), schema("area")), [])

    def test_impact_out_of_range_is_reported(self):
        doc = load("ux.json")
        doc["findings"][0]["impact"] = 7
        errors = validate(doc, schema("area"))
        self.assertTrue(any("impact" in e for e in errors), errors)

    def test_missing_title_is_reported(self):
        doc = load("ux.json")
        del doc["findings"][0]["title"]
        errors = validate(doc, schema("area"))
        self.assertTrue(any("title" in e for e in errors), errors)

    def test_top10_with_eleven_items_is_rejected(self):
        doc = load("top10.json")
        doc["items"] = [copy.deepcopy(doc["items"][0]) for _ in range(11)]
        self.assertTrue(validate(doc, schema("top10")))

    def test_null_pin_is_accepted(self):
        doc = load("ux.json")
        doc["findings"][0]["pin"] = None
        self.assertEqual(validate(doc, schema("area")), [])

    def test_area_checks_must_cover_rubric(self):
        doc = load("ux.json")
        doc["checks"] = doc["checks"][1:]
        errors = validate_findings.rubric_errors("ux", doc)
        self.assertTrue(any("ux-value-prop" in e for e in errors), errors)

    def test_area_check_accepts_partial(self):
        doc = load("ux.json")
        doc["checks"][0]["result"] = "partial"
        self.assertEqual(validate(doc, schema("area")), [])

    def test_area_check_result_enum(self):
        doc = load("ux.json")
        doc["checks"][0]["result"] = "maybe"
        self.assertTrue(validate(doc, schema("area")))

    def test_validate_dir_flags_only_bad_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / "findings"
            shutil.copytree(FIXTURES / "audit" / "findings", d)
            bad = load("a11y.json")
            bad["findings"][0]["effort"] = "Enorme"
            (d / "a11y.json").write_text(json.dumps(bad), encoding="utf-8")
            result = validate_findings.validate_dir(d)
            self.assertEqual([k for k, v in result.items() if v], ["a11y.json"])


if __name__ == "__main__":
    unittest.main()
