import os
import tempfile
import unittest

from config import load_config


class TestConfig(unittest.TestCase):
    def test_defaults(self):
        cfg = load_config()
        self.assertEqual(cfg["limit"], 10)

    def test_reads_file(self):
        fd, path = tempfile.mkstemp(suffix=".cfg")
        os.close(fd)
        with open(path, "w", encoding="utf-8") as f:
            f.write("limit=3\n")
        try:
            cfg = load_config(path)
            self.assertEqual(cfg["limit"], 3)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
