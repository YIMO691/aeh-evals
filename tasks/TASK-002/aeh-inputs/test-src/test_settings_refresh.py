import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from settings import get


class TestSettingsRefresh(unittest.TestCase):
    def test_changed_file_is_reloaded(self):
        fd, path = tempfile.mkstemp(suffix=".ini")
        os.close(fd)
        try:
            with open(path, "w", encoding="utf-8") as stream:
                stream.write("host=old\n")
            self.assertEqual(get(path, "host"), "old")
            with open(path, "w", encoding="utf-8") as stream:
                stream.write("host=new\n")
            self.assertEqual(get(path, "host"), "new")
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
