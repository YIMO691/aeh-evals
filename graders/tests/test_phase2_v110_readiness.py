import copy
import os
import unittest

from aeh_eval_grader import phase2_v110_readiness as readiness


class TestPhase2V110Readiness(unittest.TestCase):
    def test_repository_package_passes(self):
        result = readiness.compute()
        self.assertEqual(result["verdict"], "PHASE_2_V1_10_READINESS_PASS", result["errors"])
        self.assertEqual(result["planned_runs"], 72)
        self.assertFalse(result["phase2_authorized"])

    def test_schedule_preserves_inherited_order(self):
        schedule = readiness.v19.v18.v17._load("protocol/phase2-v1.10/SCHEDULE.yaml")
        self.assertEqual(schedule["blocks"], readiness.v19.v18.v17.expected_blocks(schedule["seed"]))
        self.assertEqual(schedule["blocks"][0]["groups"], ["G3", "G1", "G2", "G0"])

    def test_capture_contract_tamper_is_rejected(self):
        baseline = copy.deepcopy(readiness.v19.v18.v17._load("protocol/phase2-v1.10/BASELINE.yaml"))
        baseline["transcript_capture"]["encoding"] = "locale"
        self.assertTrue(readiness.validate_baseline(baseline))

    def test_manifest_is_canonical(self):
        path = os.path.join(readiness.repo_root(), "protocol", "phase2-v1.10", "INPUTS.sha256")
        with open(path, "r", encoding="utf-8") as stream:
            committed = stream.read().replace("\r\n", "\n")
        self.assertEqual(committed, readiness.render_input_manifest())

    def test_correction_basis_is_pinned(self):
        baseline = readiness.v19.v18.v17._load("protocol/phase2-v1.10/BASELINE.yaml")
        self.assertFalse(readiness.validate_correction_basis(baseline["correction_basis"]))


if __name__ == "__main__":
    unittest.main()
