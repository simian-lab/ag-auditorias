import unittest

from tests._helpers import PLUGIN

REFS = PLUGIN / "skills" / "simian-web-audit" / "references"
AGENTS = ["ux", "a11y", "visual", "tech", "ui-critique", "redesign", "benchmark", "seo", "presence", "load-film"]
NO_SCHEMA = {"redesign", "load-film"}
SCHEMA_OF = {"ux": "area", "a11y": "area", "visual": "area", "tech": "area"}
OUTPUT_OF = {"redesign": "report/assets/redesign-desktop.png", "load-film": "raw/bench-"}


class ReferencesTest(unittest.TestCase):
    def test_every_agent_has_reference_and_schema(self):
        for name in AGENTS:
            ref = REFS / "agents" / f"{name}.md"
            self.assertTrue(ref.exists(), name)
            text = ref.read_text(encoding="utf-8")
            self.assertIn(OUTPUT_OF.get(name, f"findings/{name}.json"), text, name)
            if name not in NO_SCHEMA:
                self.assertTrue((PLUGIN / "schemas" / f"{SCHEMA_OF.get(name, name)}.schema.json").exists(), name)

    def test_scored_agents_must_fill_rubric_checks(self):
        for name in ["ux", "a11y", "visual", "tech", "seo"]:
            text = (REFS / "agents" / f"{name}.md").read_text(encoding="utf-8")
            self.assertIn("config/rubric.json", text, name)
            self.assertIn('"checks"', text, name)
        self.assertIn('"checks"', (REFS / "brief-template.md").read_text(encoding="utf-8"))

    def test_shared_references_exist(self):
        for name in ["synthesis.md", "openseo.md", "brief-template.md"]:
            self.assertTrue((REFS / name).exists(), name)

    def test_references_have_no_absolute_paths(self):
        for f in REFS.rglob("*.md"):
            self.assertNotIn("/Users/", f.read_text(encoding="utf-8"), f.name)

    def test_references_do_not_depend_on_source_skills(self):
        for f in REFS.rglob("*.md"):
            text = f.read_text(encoding="utf-8")
            for src in ["seo-geo", "ai-seo", "ui-taste", "web-design-guidelines", "ui-ux-pro-max"]:
                self.assertNotIn(src, text, f"{f.name} mentions {src}")


if __name__ == "__main__":
    unittest.main()
