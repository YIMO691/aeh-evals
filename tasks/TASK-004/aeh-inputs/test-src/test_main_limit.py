import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from main import run


class TestMainLimit(unittest.TestCase):
    def test_config_limit_is_honored(self):
        fd, path = tempfile.mkstemp(suffix=".cfg")
        os.close(fd)
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("limit=2\n")
            self.assertEqual(run([1, 2, 3], config_path=path), [1, 2])
        finally:
            os.unlink(path)

    def test_default_limit_keeps_all(self):
        self.assertEqual(run([1, 2, 3]), [1, 2, 3])


if __name__ == "__main__":
    unittest.main()
