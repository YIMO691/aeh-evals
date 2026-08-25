import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from pager import paginate


class TestPagerContract(unittest.TestCase):
    def test_one_based_pages(self):
        values = list(range(10))
        self.assertEqual(paginate(values, 1, 3), [0, 1, 2])
        self.assertEqual(paginate(values, 3, 3), [6, 7, 8])
        self.assertEqual(paginate(values, 4, 3), [9])


if __name__ == "__main__":
    unittest.main()
