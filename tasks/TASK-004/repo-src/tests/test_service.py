import unittest

from service import top_items


class TestService(unittest.TestCase):
    def test_default_limit(self):
        self.assertEqual(top_items([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    def test_explicit_limit(self):
        self.assertEqual(top_items([1, 2, 3], limit=2), [1, 2])


if __name__ == "__main__":
    unittest.main()
