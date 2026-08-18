"""奖励领取服务。"""


class DuplicateClaimError(Exception):
    pass


class RewardService:
    def __init__(self, wallet, ledger):
        self.wallet = wallet
        self.ledger = ledger

    def claim(self, user, claim_id, amount):
        """领取奖励：入账并记录流水。"""
        self.wallet.credit(amount)
        self.ledger.record(claim_id, user, amount)
