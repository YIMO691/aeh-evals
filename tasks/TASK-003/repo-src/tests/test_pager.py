import unittest

from pager import paginate


class TestPager(unittest.TestCase):
    def test_rejects_bad_page(self):
        with self.assertRaises(ValueError):
            paginate([1, 2, 3], 0, 2)

    def test_rejects_bad_size(self):
        with self.assertRaises(ValueError):
            paginate([1, 2, 3], 1, 0)


if __name__ == "__main__":
    unittest.main()
