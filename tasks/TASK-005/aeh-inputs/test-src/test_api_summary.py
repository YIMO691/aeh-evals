import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from api import get_summary
from storage import Store


class TestApiSummary(unittest.TestCase):
    def test_summary_and_empty_store(self):
        store = Store()
        self.assertEqual(get_summary(store), {"count": 0, "total": 0})
        store.add({"kind": "a", "amount": 10})
        store.add({"kind": "b", "amount": 20})
        self.assertEqual(get_summary(store), {"count": 2, "total": 30})


if __name__ == "__main__":
    unittest.main()
