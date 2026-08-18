import unittest

from api import list_records
from storage import Store


class TestApi(unittest.TestCase):
    def test_list_records(self):
        store = Store()
        store.add({"kind": "a", "amount": 1})
        self.assertEqual(list_records(store), [{"kind": "a", "amount": 1}])


if __name__ == "__main__":
    unittest.main()
