import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from pricing import format_price


class TestFormatPriceContract(unittest.TestCase):
    def test_two_decimal_contract(self):
        self.assertEqual(format_price(0), "0.00")
        self.assertEqual(format_price(100), "1.00")
        self.assertEqual(format_price(1200), "12.00")
        self.assertEqual(format_price(1), "0.01")


if __name__ == "__main__":
    unittest.main()
