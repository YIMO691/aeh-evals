import unittest

from pager import paginate


class TestPagerHidden(unittest.TestCase):
    def test_first_page(self):
        self.assertEqual(paginate(list(range(10)), 1, 3), [0, 1, 2])

    def test_last_partial_page(self):
        self.assertEqual(paginate(list(range(10)), 4, 3), [9])

    def test_middle_page(self):
        self.assertEqual(paginate(list(range(10)), 3, 3), [6, 7, 8])


if __name__ == "__main__":
    unittest.main()
