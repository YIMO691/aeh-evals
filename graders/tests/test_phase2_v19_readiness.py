import copy
import os
import unittest

from aeh_eval_grader import phase2_v19_readiness as readiness


class TestPhase2V19Readiness(unittest.TestCase):
    def test_repository_package_detects_shared_input_drift_after_v110(self):
        result = readiness.compute()
        self.assertEqual(result["verdict"], "PHASE_2_V1_9_READINESS_FAIL")
        self.assertTrue(any("g3_runner.py" in error for error in result["errors"]))
        self.assertEqual(result["planned_runs"], 72)
        self.assertFalse(result["phase2_authorized"])

    def test_schedule_preserves_inherited_order(self):
        schedule = readiness.v18.v17._load("protocol/phase2-v1.9/SCHEDULE.yaml")
        self.assertEqual(schedule["blocks"], readiness.v18.v17.expected_blocks(schedule["seed"]))
        self.assertEqual(schedule["blocks"][0]["groups"], ["G3", "G1", "G2", "G0"])

    def test_misplaced_approval_policy_is_rejected(self):
        baseline = copy.deepcopy(readiness.v18.v17._load("protocol/phase2-v1.9/BASELINE.yaml"))
        argv = baseline["codex_execution"]["argv_prefix"]
        del argv[0:2]
        insert_at = argv.index("exec") + 1
        argv[insert_at:insert_at] = ["--ask-for-approval", "never"]
        self.assertTrue(readiness.validate_baseline(baseline))

    def test_windows_helper_override_is_required(self):
        baseline = copy.deepcopy(readiness.v18.v17._load("protocol/phase2-v1.9/BASELINE.yaml"))
        argv = baseline["codex_execution"]["argv_prefix"]
        config_index = argv.index("--config")
        del argv[config_index:config_index + 2]
        self.assertTrue(readiness.validate_baseline(baseline))

    def test_historical_manifest_digest_remains_immutable(self):
        baseline = readiness.v18.v17._load("protocol/phase2-v1.9/BASELINE.yaml")
        path = os.path.join(readiness.repo_root(), *baseline["input_manifest"]["path"].split("/"))
        self.assertEqual(readiness.v18.v17._sha256_file(path), baseline["input_manifest"]["sha256"])

    def test_correction_basis_is_pinned(self):
        baseline = readiness.v18.v17._load("protocol/phase2-v1.9/BASELINE.yaml")
        self.assertFalse(readiness.validate_correction_basis(baseline["correction_basis"]))


if __name__ == "__main__":
    unittest.main()
