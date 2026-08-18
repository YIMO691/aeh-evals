import unittest

from pricing import apply_discount, clamp_percent, format_price


class TestPricing(unittest.TestCase):
    def test_clamp_bounds(self):
        self.assertEqual(clamp_percent(-5), 0)
        self.assertEqual(clamp_percent(150), 100)

    def test_apply_discount_fraction(self):
        self.assertEqual(apply_discount(100.0, 25), 75.0)

    def test_format_price_fraction(self):
        self.assertEqual(format_price(1234), "12.34")


if __name__ == "__main__":
    unittest.main()
