import unittest

from aeh_eval_grader.diff import scope_violations


class TestDiff(unittest.TestCase):
    def test_exact_path_allowed(self):
        self.assertEqual(scope_violations(["src/a.py"], ["src/a.py"]), [])

    def test_directory_prefix_allowed(self):
        self.assertEqual(scope_violations(["src/a.py"], ["src/"]), [])

    def test_out_of_scope_violation(self):
        self.assertEqual(scope_violations(["src/b.py"], ["src/a.py"]), ["src/b.py"])

    def test_glob_allowed(self):
        self.assertEqual(scope_violations(["src/a.py", "src/c.py"], ["src/*.py"]), [])

    def test_glob_denies_nonmatching(self):
        self.assertEqual(scope_violations(["docs/x.md"], ["src/*.py"]), ["docs/x.md"])

    def test_windows_separators_normalized(self):
        self.assertEqual(scope_violations([r"src\a.py"], ["src/a.py"]), [])


if __name__ == "__main__":
    unittest.main()
