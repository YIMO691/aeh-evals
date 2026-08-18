import os
import tempfile
import unittest

from main import run


class TestMainHidden(unittest.TestCase):
    def test_config_limit_is_honored(self):
        fd, path = tempfile.mkstemp(suffix=".cfg")
        os.close(fd)
        with open(path, "w", encoding="utf-8") as f:
            f.write("limit=2\n")
        try:
            result = run([1, 2, 3, 4, 5], config_path=path)
            self.assertEqual(result, [1, 2])
        finally:
            os.unlink(path)

    def test_default_when_no_config(self):
        self.assertEqual(run([1, 2, 3]), [1, 2, 3])


if __name__ == "__main__":
    unittest.main()
