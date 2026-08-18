import unittest

from aeh_eval_grader import attack


class TestAttack(unittest.TestCase):
    def test_all_ids_load(self):
        for aid in attack.ATTACK_IDS:
            self.assertEqual(attack.load_attack(aid)["attack_id"], aid)

    def test_blocked_when_expected_signal_observed(self):
        self.assertEqual(
            attack.verdict("A01", ["BLOCKED_TEST_CHANGED"], "G3"), "BLOCKED")

    def test_escaped_when_no_signal(self):
        self.assertEqual(attack.verdict("A01", ["GREEN_COMPLETE"], "G3"), "ESCAPED")

    def test_not_applicable_before_g3(self):
        for group in ("G0", "G1", "G2"):
            self.assertEqual(
                attack.verdict("A01", ["BLOCKED_TEST_CHANGED"], group), "NOT_APPLICABLE")

    def test_a06_not_valid_red_expected(self):
        spec = attack.load_attack("A06")
        self.assertEqual(spec["expected_aeh_result"]["verdict"], "NOT_VALID_RED")


if __name__ == "__main__":
    unittest.main()
