"""Deterministic repository restoration from task bundles."""
import os
import shutil
import subprocess

import yaml


def load_task(task_dir):
    with open(os.path.join(task_dir, "task.yaml"), "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def restore_bundle(task_dir, workdir):
    """Clone the task bundle and check out the frozen SHA.

    Returns {"ok": bool, "head": str, "expected": str, "dirty": str, "detail": str}.
    """
    task = load_task(task_dir)
    expected = task["repository"]["commit"]
    bundle = os.path.join(task_dir, "repo-src.bundle")
    if not os.path.isfile(bundle):
        return {"ok": False, "head": None, "expected": expected,
                "dirty": "", "detail": "bundle missing: " + bundle}
    if os.path.exists(workdir):
        if os.listdir(workdir):
            return {"ok": False, "head": None, "expected": expected,
                    "dirty": "", "detail": "workdir exists and is not empty: " + workdir}
        shutil.rmtree(workdir)
    proc = subprocess.run(["git", "clone", "-q", bundle, workdir],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        return {"ok": False, "head": None, "expected": expected,
                "dirty": "", "detail": "clone failed: " + proc.stderr.strip()}
    proc = subprocess.run(["git", "-C", workdir, "checkout", "-q", expected],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        return {"ok": False, "head": None, "expected": expected,
                "dirty": "", "detail": "checkout failed: " + proc.stderr.strip()}
    head = subprocess.run(["git", "-C", workdir, "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "-C", workdir, "status", "--porcelain"],
                           capture_output=True, text=True).stdout.strip()
    ok = (head == expected and dirty == "")
    return {"ok": ok, "head": head, "expected": expected, "dirty": dirty,
            "detail": "RESTORE_OK" if ok else "RESTORE_FAIL"}


def verify_restore(workdir, expected_sha):
    """Verify an existing workdir is at the frozen SHA and clean.

    Used for INVALID_RUN detection (dirty tree or wrong SHA).
    """
    if not os.path.isdir(os.path.join(workdir, ".git")):
        return {"ok": False, "detail": "not a git workdir: " + workdir}
    head = subprocess.run(["git", "-C", workdir, "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "-C", workdir, "status", "--porcelain"],
                           capture_output=True, text=True).stdout.strip()
    ok = (head == expected_sha and dirty == "")
    return {"ok": ok, "head": head, "expected": expected_sha, "dirty": dirty,
            "detail": "VERIFY_OK" if ok else "INVALID_RUN"}
