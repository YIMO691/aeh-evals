import unittest

from storage import Store


class TestStorage(unittest.TestCase):
    def test_add_keeps_order(self):
        store = Store()
        store.add({"kind": "a", "amount": 1})
        store.add({"kind": "b", "amount": 2})
        self.assertEqual([r["kind"] for r in store.records], ["a", "b"])


if __name__ == "__main__":
    unittest.main()
