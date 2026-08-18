import unittest

from api import get_summary
from storage import Store


class TestApiHidden(unittest.TestCase):
    def test_summary_totals(self):
        store = Store()
        store.add({"kind": "a", "amount": 10})
        store.add({"kind": "b", "amount": 20})
        summary = get_summary(store)
        self.assertEqual(summary["count"], 2)
        self.assertEqual(summary["total"], 30)

    def test_summary_empty(self):
        store = Store()
        summary = get_summary(store)
        self.assertEqual(summary, {"count": 0, "total": 0})


if __name__ == "__main__":
    unittest.main()
