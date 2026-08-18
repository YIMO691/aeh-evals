"""用户余额账户（内存实现，流水持久化见 ledger）。"""


class Wallet:
    def __init__(self):
        self.balance = 0

    def credit(self, amount):
        if amount <= 0:
            raise ValueError("amount must be positive")
        self.balance += amount
