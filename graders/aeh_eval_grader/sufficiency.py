"""Run bundle self-sufficiency check."""
import os

REQUIRED_FILES = [
    "run.yaml",
    "evidence/session.log",
    "evidence/git-diff.txt",
    "evidence/tests-output.txt",
    "evidence/grader-output.txt",
]


def check_sufficiency(run_dir):
    """Return {"ok": bool, "missing": [...]}."""
    missing = [f for f in REQUIRED_FILES if not os.path.isfile(os.path.join(run_dir, f))]
    return {"ok": not missing, "missing": missing}
