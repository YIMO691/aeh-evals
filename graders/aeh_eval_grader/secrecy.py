"""Hidden-test secrecy scanning for run artifacts (v1.4 semantics).

Only agent-visible material is scanned:
  - the agent worktree
  - evidence/session.log and evidence/agent-last-message.txt
Operator/grader artifacts (grader-output.txt, hidden-tests-output.txt) are excluded.
"""
import os

CONTENT_MARKERS = [
    "hidden-tests",
    "hidden_tests",
    "ground_truth",
    "expected_aeh_result",
]


def _filename_leaks_hidden(fn):
    low = fn.lower()
    return ("hidden" in low) or (low.startswith("test_") and low.endswith(".py") and "_hidden" in low)


def scan_text(text):
    """Return content-marker hits in a text block."""
    hits = []
    for line in text.splitlines():
        low = line.strip().lower()
        for marker in CONTENT_MARKERS:
            if marker.lower() in low:
                hits.append((marker, line.strip()[:160]))
    return hits


def _scan_file(path, rel):
    hits = []
    if _filename_leaks_hidden(os.path.basename(path)):
        hits.append(rel + ": filename-leak")
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read(200000)
    except OSError:
        return hits
    for marker, line in scan_text(text):
        hits.append(rel + ": content-marker-" + marker + " :: " + line)
    return hits


def _scan_worktree(root):
    hits = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__", ".aeh")]
        for fn in filenames:
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, root)
            hits.extend(_scan_file(path, rel))
    return hits


def check_run_secrecy(run_dir):
    """Return {"leak": bool, "hits": [...]}."""
    hits = []
    work = os.path.join(run_dir, "work")
    if os.path.isdir(work):
        hits.extend(_scan_worktree(work))
    for rel in ("evidence/session.log", "evidence/agent-last-message.txt"):
        path = os.path.join(run_dir, rel)
        if os.path.isfile(path):
            hits.extend(_scan_file(path, rel))
    return {"leak": bool(hits), "hits": hits}
