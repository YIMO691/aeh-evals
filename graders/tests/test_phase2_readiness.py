import copy
import os
import tempfile
import unittest

from aeh_eval_grader import phase2_readiness


class TestPhase2Readiness(unittest.TestCase):
    def test_repository_package_detects_shared_input_drift_after_v18(self):
        result = phase2_readiness.compute()
        self.assertEqual(result["verdict"], "PHASE_2_READINESS_FAIL")
        self.assertTrue(any("g3_runner.py" in error for error in result["errors"]))
        self.assertTrue(any("graders/cli.py" in error for error in result["errors"]))
        self.assertEqual(result["planned_runs"], 72)
        self.assertFalse(result["phase2_authorized"])

    def test_schedule_is_stratified_and_deterministic(self):
        blocks = phase2_readiness.expected_blocks("AEH-PHASE2-V1.7-20260825")
        self.assertEqual(len(blocks), 18)
        self.assertEqual(
            {(block["task_id"], block["repetition"]) for block in blocks},
            {(task, repetition) for task in phase2_readiness.EXPECTED_TASKS
             for repetition in phase2_readiness.EXPECTED_REPETITIONS},
        )
        for block in blocks:
            self.assertEqual(set(block["groups"]), set(phase2_readiness.EXPECTED_GROUPS))

    def test_schedule_tamper_is_detected(self):
        schedule = {
            "protocol_version": "1.7",
            "seed": "AEH-PHASE2-V1.7-20260825",
            "blocks": phase2_readiness.expected_blocks("AEH-PHASE2-V1.7-20260825"),
        }
        schedule = copy.deepcopy(schedule)
        schedule["blocks"][0]["groups"].reverse()
        self.assertTrue(phase2_readiness.validate_schedule(schedule))

    def test_authorization_tamper_is_detected(self):
        baseline = phase2_readiness._load("protocol/phase2-v1.7/BASELINE.yaml")
        baseline = copy.deepcopy(baseline)
        baseline["phase2_72_run"]["authorized"] = True
        self.assertIn("Phase 2 must remain unauthorized", phase2_readiness.validate_baseline(baseline))

    def test_input_manifest_covers_all_task_treatments(self):
        baseline = phase2_readiness._load("protocol/phase2-v1.7/BASELINE.yaml")
        path = os.path.join(phase2_readiness.repo_root(), *baseline["input_manifest"]["path"].split("/"))
        with open(path, "r", encoding="utf-8") as stream:
            paths = {line.strip().split(None, 1)[1] for line in stream if line.strip()}
        for task_id in phase2_readiness.EXPECTED_TASKS:
            prefix = "tasks/%s/aeh-inputs/" % task_id
            self.assertTrue({
                prefix + "reqs.yaml",
                prefix + "plan.yaml",
                prefix + "scope-v1.7.yaml",
            }.issubset(paths))

    def test_committed_input_manifest_is_canonical(self):
        baseline = phase2_readiness._load("protocol/phase2-v1.7/BASELINE.yaml")
        path = os.path.join(phase2_readiness.repo_root(), *baseline["input_manifest"]["path"].split("/"))
        self.assertEqual(
            phase2_readiness._sha256_file(path),
            baseline["input_manifest"]["sha256"],
        )

    def test_text_digest_is_line_ending_independent(self):
        with tempfile.TemporaryDirectory() as tmp:
            lf = os.path.join(tmp, "lf.txt")
            crlf = os.path.join(tmp, "crlf.txt")
            with open(lf, "wb") as stream:
                stream.write(b"one\ntwo\n")
            with open(crlf, "wb") as stream:
                stream.write(b"one\r\ntwo\r\n")
            self.assertEqual(
                phase2_readiness._sha256_file(lf),
                phase2_readiness._sha256_file(crlf),
            )


if __name__ == "__main__":
    unittest.main()
