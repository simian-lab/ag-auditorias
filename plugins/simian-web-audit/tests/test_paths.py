import unittest
from pathlib import Path

from tests._helpers import PLUGIN  # noqa: F401
from lib import paths


class PathsTest(unittest.TestCase):
    def test_plugin_root_is_parent_of_scripts(self):
        self.assertTrue((paths.plugin_root() / ".claude-plugin" / "plugin.json").exists())

    def test_audits_root_uses_base(self):
        self.assertEqual(paths.audits_root(Path("/tmp/x")), Path("/tmp/x/audits"))

    def test_audits_root_defaults_to_cwd(self):
        self.assertEqual(paths.audits_root(), Path.cwd() / "audits")


if __name__ == "__main__":
    unittest.main()
