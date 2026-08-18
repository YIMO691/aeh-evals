import os
import unittest

import yaml

from aeh_eval_grader import manifest
from aeh_eval_grader.paths import repo_root


class TestManifest(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(repo_root(), "protocol", "examples", "run.example.yaml"),
                  "r", encoding="utf-8") as f:
            self.example = yaml.safe_load(f)

    def test_example_is_valid(self):
        ok, errors = manifest.validate_run(self.example)
        self.assertTrue(ok, errors)

    def test_missing_field_invalid(self):
        run = dict(self.example)
        run.pop("agent")
        ok, errors = manifest.validate_run(run)
        self.assertFalse(ok)
        self.assertTrue(any("agent" in e for e in errors))

    def test_bad_group_invalid(self):
        run = dict(self.example)
        run["group"] = "G9"
        ok, _ = manifest.validate_run(run)
        self.assertFalse(ok)

    def test_freeze_compare_detects_mismatch(self):
        other = dict(self.example)
        other["agent"] = dict(other["agent"])
        other["agent"]["model"] = "other-model"
        mismatches = manifest.compare_freeze(self.example, other)
        self.assertTrue(any(k == "agent.model" for k, _, _ in mismatches))

    def test_freeze_compare_equal(self):
        self.assertEqual(manifest.compare_freeze(self.example, dict(self.example)), [])


if __name__ == "__main__":
    unittest.main()
