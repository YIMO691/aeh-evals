import unittest

from ledger import Ledger
from rewards import RewardService
from wallet import Wallet


class TestRewards(unittest.TestCase):
    def test_single_claim(self):
        wallet = Wallet()
        ledger = Ledger()
        service = RewardService(wallet, ledger)
        service.claim("alice", "CLAIM-1", 100)
        self.assertEqual(wallet.balance, 100)
        self.assertTrue(ledger.has("CLAIM-1"))


if __name__ == "__main__":
    unittest.main()
