import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from ledger import Ledger
from rewards import DuplicateClaimError, RewardService
from wallet import Wallet


class TestRewardIdempotency(unittest.TestCase):
    def test_duplicate_rejected_and_distinct_claim_allowed(self):
        wallet = Wallet()
        ledger = Ledger()
        service = RewardService(wallet, ledger)
        service.claim("alice", "CLAIM-1", 100)
        with self.assertRaises(DuplicateClaimError):
            service.claim("alice", "CLAIM-1", 100)
        service.claim("alice", "CLAIM-2", 50)
        self.assertEqual(wallet.balance, 150)
        self.assertEqual(len(ledger.entries), 2)


if __name__ == "__main__":
    unittest.main()
