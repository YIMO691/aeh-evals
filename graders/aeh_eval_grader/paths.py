"""Helpers to locate the aeh-evals repository root without hard-coded paths."""
import os


def repo_root(start=None):
    """Return the aeh-evals repository root by locating protocol/PROTOCOL.md."""
    cur = os.path.abspath(start or os.path.dirname(__file__))
    for _ in range(10):
        if os.path.isfile(os.path.join(cur, "protocol", "PROTOCOL.md")):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    raise RuntimeError("aeh-evals repository root not found from " + str(start))
