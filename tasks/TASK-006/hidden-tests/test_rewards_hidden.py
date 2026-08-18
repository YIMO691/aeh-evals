import unittest

from ledger import Ledger
from rewards import DuplicateClaimError, RewardService
from wallet import Wallet


class TestRewardsHidden(unittest.TestCase):
    def setUp(self):
        self.wallet = Wallet()
        self.ledger = Ledger()
        self.service = RewardService(self.wallet, self.ledger)

    def test_duplicate_claim_rejected(self):
        self.service.claim("alice", "CLAIM-1", 100)
        with self.assertRaises(DuplicateClaimError):
            self.service.claim("alice", "CLAIM-1", 100)
        self.assertEqual(self.wallet.balance, 100)
        self.assertEqual(len(self.ledger.entries), 1)

    def test_distinct_claims_allowed(self):
        self.service.claim("alice", "CLAIM-1", 100)
        self.service.claim("alice", "CLAIM-2", 50)
        self.assertEqual(self.wallet.balance, 150)
        self.assertEqual(len(self.ledger.entries), 2)


if __name__ == "__main__":
    unittest.main()
