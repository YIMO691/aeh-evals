import unittest

from aeh_eval_grader import report


class TestReport(unittest.TestCase):
    def test_empty_matrix_has_header(self):
        csv_text = report.evidence_matrix([])
        self.assertIn("task_id,G0,G1,G2,G3,G4,aeh_gain", csv_text)

    def test_single_run_row(self):
        run = ("RUN-0001", {
            "task_id": "TASK-001",
            "group": "G3",
            "result": {"status": "COMPLETED", "outcome": "BLOCKED"},
        })
        csv_text = report.evidence_matrix([run])
        self.assertIn("TASK-001", csv_text)
        self.assertIn("BLOCKED", csv_text)

    def test_aborted_run_skipped(self):
        run = ("RUN-0002", {
            "task_id": "TASK-001",
            "group": "G3",
            "result": {"status": "ABORTED", "outcome": ""},
        })
        csv_text = report.evidence_matrix([run])
        self.assertNotIn("TASK-001", csv_text)


if __name__ == "__main__":
    unittest.main()
