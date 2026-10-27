import unittest

from tests._helpers import PLUGIN  # noqa: F401
from lib import units


class UnitsTest(unittest.TestCase):
    def test_mb_from_kib_uses_1024_and_comma(self):
        self.assertEqual(units.mb_from_kib(13714), "13,4 MB")

    def test_mb_from_kib_small_value(self):
        self.assertEqual(units.mb_from_kib(512), "0,5 MB")

    def test_seconds_from_ms(self):
        self.assertEqual(units.seconds(8100), "8,1 s")

    def test_seconds_rounds(self):
        self.assertEqual(units.seconds(65249), "65,2 s")


if __name__ == "__main__":
    unittest.main()
