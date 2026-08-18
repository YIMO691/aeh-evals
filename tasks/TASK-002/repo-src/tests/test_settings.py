import os
import tempfile
import unittest

from settings import get, load_settings


class TestSettings(unittest.TestCase):
    def setUp(self):
        fd, self.path = tempfile.mkstemp(suffix=".ini")
        os.close(fd)
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("# comment\nhost=localhost\nport=8080\n")

    def tearDown(self):
        os.unlink(self.path)

    def test_first_read(self):
        data = load_settings(self.path)
        self.assertEqual(data["host"], "localhost")
        self.assertEqual(data["port"], "8080")

    def test_comments_ignored(self):
        data = load_settings(self.path)
        self.assertNotIn("# comment", data)

    def test_get_default(self):
        self.assertEqual(get(self.path, "missing", "fallback"), "fallback")


if __name__ == "__main__":
    unittest.main()
