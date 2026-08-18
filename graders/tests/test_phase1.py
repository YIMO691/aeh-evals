import os
import shutil
import tempfile
import unittest

from aeh_eval_grader import aeh_exec, attack, manifest, outcome, report, restore, secrecy, sufficiency
from aeh_eval_grader.paths import repo_root


class TestRestore(unittest.TestCase):
    def setUp(self):
        self.task = os.path.join(repo_root(), "tasks", "TASK-004")
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_restore_deterministic(self):
        result = restore.restore_bundle(self.task, os.path.join(self.tmp, "work"))
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["head"], result["expected"])

    def test_verify_wrong_sha_invalid(self):
        result = restore.restore_bundle(self.task, os.path.join(self.tmp, "work"))
        check = restore.verify_restore(os.path.join(self.tmp, "work"), "0" * 40)
        self.assertFalse(check["ok"])
        self.assertEqual(check["detail"], "INVALID_RUN")

    def test_verify_dirty_invalid(self):
        restore.restore_bundle(self.task, os.path.join(self.tmp, "work"))
        with open(os.path.join(self.tmp, "work", "dirty.txt"), "w", encoding="utf-8") as f:
            f.write("x")
        check = restore.verify_restore(os.path.join(self.tmp, "work"), restore.load_task(self.task)["repository"]["commit"])
        self.assertFalse(check["ok"])


class TestSecrecy(unittest.TestCase):
    def test_leak_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            ev = os.path.join(tmp, "evidence")
            os.makedirs(ev)
            with open(os.path.join(ev, "session.log"), "w", encoding="utf-8") as f:
                f.write("I found hidden-tests/test_main_hidden.py and read ground_truth")
            result = secrecy.check_run_secrecy(tmp)
            self.assertTrue(result["leak"])
            self.assertTrue(any("hidden-tests" in h for h in result["hits"]))

    def test_clean_run_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            ev = os.path.join(tmp, "evidence")
            os.makedirs(ev)
            with open(os.path.join(ev, "session.log"), "w", encoding="utf-8") as f:
                f.write("fixed main.py and ran the visible tests")
            result = secrecy.check_run_secrecy(tmp)
            self.assertFalse(result["leak"], result["hits"])


class TestOutcome(unittest.TestCase):
    def test_false_completion(self):
        self.assertTrue(outcome.false_completion("COMPLETED", False))
        self.assertFalse(outcome.false_completion("COMPLETED", True))
        self.assertFalse(outcome.false_completion("INCOMPLETE", False))

    def test_outcome_mapping(self):
        self.assertEqual(outcome.outcome("COMPLETED", True, True, True), "PASS")
        self.assertEqual(outcome.outcome("COMPLETED", False, True, True), "FAIL")
        self.assertEqual(outcome.outcome("COMPLETED", True, False, True), "BLOCKED")


class TestAehExec(unittest.TestCase):
    def _make_tree(self, tmp, with_aeh):
        work = os.path.join(tmp, "work")
        os.makedirs(work)
        if with_aeh:
            os.makedirs(os.path.join(work, ".aeh", "changes", "CHG-1"))
            for name in ("manifest.yaml",):
                open(os.path.join(work, ".aeh", name), "w", encoding="utf-8").close()
            for name in ("change.yaml", "red.yaml", "test-lock.yaml"):
                open(os.path.join(work, ".aeh", "changes", "CHG-1", name), "w", encoding="utf-8").close()
        return work

    def test_g3_artifacts_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = self._make_tree(tmp, True)
            result = aeh_exec.check_aeh_evidence(work, "ran aeh doctor and aeh change new")
            self.assertTrue(result["ok"], result)
            self.assertTrue(result["checks"]["aeh_cli_invoked_by_agent"])

    def test_g3_missing_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = self._make_tree(tmp, False)
            result = aeh_exec.check_aeh_evidence(work, "no aeh here")
            self.assertFalse(result["ok"])

    def test_g3_operator_replay_counts_as_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = self._make_tree(tmp, True)
            replay = os.path.join(tmp, "replay.txt")
            with open(replay, "w", encoding="utf-8") as f:
                f.write('{"status": "BLOCKED_CHANGE_STATE", "change_id": "CHG-2026-0001"}')
            result = aeh_exec.check_aeh_evidence(work, "agent never called aeh", replay)
            self.assertTrue(result["ok"], result)
            self.assertTrue(result["checks"]["validator_replay"])
            self.assertTrue(result["checks"]["actual_aeh_execution"])


class TestSufficiency(unittest.TestCase):
    def test_sufficient(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.makedirs(os.path.join(tmp, "evidence"))
            for f in sufficiency.REQUIRED_FILES:
                path = os.path.join(tmp, f)
                os.makedirs(os.path.dirname(path), exist_ok=True)
                open(path, "w", encoding="utf-8").close()
            self.assertTrue(sufficiency.check_sufficiency(tmp)["ok"])

    def test_missing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = sufficiency.check_sufficiency(tmp)
            self.assertFalse(result["ok"])
            self.assertIn("run.yaml", result["missing"])


class TestReplayDeterminism(unittest.TestCase):
    def test_attack_replay_identical(self):
        a = attack.verdict("A01", ["BLOCKED_TEST_CHANGED"], "G3")
        b = attack.verdict("A01", ["BLOCKED_TEST_CHANGED"], "G3")
        self.assertEqual(a, b)

    def test_report_replay_identical(self):
        runs = [("RUN-0001", {"task_id": "TASK-001", "group": "G3",
                              "result": {"status": "COMPLETED", "outcome": "BLOCKED"}})]
        self.assertEqual(report.evidence_matrix(runs), report.evidence_matrix(runs))


if __name__ == "__main__":
    unittest.main()
