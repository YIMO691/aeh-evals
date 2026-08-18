"""Pagination helpers."""


def paginate(items, page, size):
    """Return the requested page of items (1-based page numbering)."""
    if page < 1:
        raise ValueError("page must be >= 1")
    if size < 1:
        raise ValueError("size must be >= 1")
    start = page * size
    return items[start:start + size]
