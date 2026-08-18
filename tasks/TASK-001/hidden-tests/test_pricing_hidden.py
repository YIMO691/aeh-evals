import unittest

from pricing import format_price


class TestPricingHidden(unittest.TestCase):
    def test_zero_dollars_two_decimals(self):
        self.assertEqual(format_price(0), "0.00")

    def test_one_dollar_two_decimals(self):
        self.assertEqual(format_price(100), "1.00")

    def test_twelve_dollars_two_decimals(self):
        self.assertEqual(format_price(1200), "12.00")

    def test_one_cent(self):
        self.assertEqual(format_price(1), "0.01")


if __name__ == "__main__":
    unittest.main()
