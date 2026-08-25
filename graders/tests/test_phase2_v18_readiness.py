import copy
import os
import unittest

from aeh_eval_grader import phase2_v18_readiness as readiness


class TestPhase2V18Readiness(unittest.TestCase):
    def test_repository_package_passes(self):
        result = readiness.compute()
        self.assertEqual(result["verdict"], "PHASE_2_V1_8_READINESS_PASS", result["errors"])
        self.assertEqual(result["planned_runs"], 72)
        self.assertFalse(result["phase2_authorized"])

    def test_schedule_preserves_inherited_order(self):
        schedule = readiness.v17._load("protocol/phase2-v1.8/SCHEDULE.yaml")
        self.assertEqual(schedule["blocks"], readiness.v17.expected_blocks(schedule["seed"]))
        self.assertEqual(schedule["blocks"][0]["groups"], ["G3", "G1", "G2", "G0"])

    def test_ignore_rules_is_rejected(self):
        baseline = copy.deepcopy(readiness.v17._load("protocol/phase2-v1.8/BASELINE.yaml"))
        baseline["codex_execution"]["flags"].append("--ignore-rules")
        self.assertTrue(readiness.validate_baseline(baseline))

    def test_headless_permission_tamper_is_rejected(self):
        reference = readiness.v17._load("protocol/phase2-v1.8/BASELINE.yaml")["g3_bootstrap_answers"]
        body = readiness.v17._load(reference["path"])
        observed = {key: value["answer"] for key, value in body["answers"].items()}
        self.assertEqual(observed, readiness.EXPECTED_ANSWERS)

    def test_manifest_is_canonical(self):
        path = os.path.join(readiness.repo_root(), "protocol", "phase2-v1.8", "INPUTS.sha256")
        with open(path, "r", encoding="utf-8") as stream:
            committed = stream.read().replace("\r\n", "\n")
        self.assertEqual(committed, readiness.render_input_manifest())


if __name__ == "__main__":
    unittest.main()

