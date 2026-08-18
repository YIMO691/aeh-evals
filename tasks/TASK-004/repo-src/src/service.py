"""List trimming service."""


def top_items(records, limit=10):
    """Return at most the first `limit` records."""
    return records[:limit]
