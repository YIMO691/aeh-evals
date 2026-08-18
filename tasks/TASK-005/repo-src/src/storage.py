"""In-memory record store."""


class Store:
    def __init__(self):
        self.records = []

    def add(self, record):
        self.records.append(dict(record))
