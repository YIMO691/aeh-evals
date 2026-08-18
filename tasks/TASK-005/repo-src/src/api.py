"""Query API over the store."""


def list_records(store):
    """Return all records in insertion order."""
    return list(store.records)
