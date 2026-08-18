import os
import tempfile
import unittest

from settings import get


class TestSettingsHidden(unittest.TestCase):
    def setUp(self):
        fd, self.path = tempfile.mkstemp(suffix=".ini")
        os.close(fd)

    def tearDown(self):
        os.unlink(self.path)

    def test_reloads_changed_file(self):
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("host=old\n")
        self.assertEqual(get(self.path, "host"), "old")
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("host=new\n")
        self.assertEqual(get(self.path, "host"), "new")


if __name__ == "__main__":
    unittest.main()
