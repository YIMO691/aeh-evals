"""领取流水账本（append-only，用于审计与幂等判定）。"""


class Ledger:
    def __init__(self):
        self.entries = []

    def record(self, claim_id, user, amount):
        self.entries.append({"claim_id": claim_id, "user": user, "amount": amount})

    def has(self, claim_id):
        return any(e["claim_id"] == claim_id for e in self.entries)
