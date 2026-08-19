"""G3 AEH evidence facts (v1.6, AMENDMENT-006).

This checker reports three machine facts and never draws the assurance
conclusion itself:

  - artifacts_present: .aeh/manifest.yaml + change.yaml + workflow artifacts
  - aeh_cli_by_agent: whether the executing agent invoked the `aeh` CLI
  - validator_replay: operator replay of the real AEH validator + its verdict
"""
import json
import os

import yaml

REQUIRED_AEH_FILES = [
    (".aeh", "manifest.yaml"),
]
REQUIRED_CHANGE_FILES = [
    ".aeh/changes/*/change.yaml",
]
WORKFLOW_ARTIFACTS = [
    "test-lock.yaml",
    "verification.yaml",
    "red.yaml",
    "scope.yaml",
]


def _glob_exists(root, pattern):
    if "*" not in pattern:
        return [os.path.join(root, pattern)] if os.path.exists(os.path.join(root, pattern)) else []
    prefix, _, suffix = pattern.partition("*")
    base = os.path.join(root, prefix)
    found = []
    if os.path.isdir(base):
        for name in os.listdir(base):
            path = os.path.join(base, name)
            if os.path.exists(os.path.join(path, suffix.lstrip("/"))):
                found.append(os.path.join(path, suffix.lstrip("/")))
    return found


def _replay_verdict(replay_file):
    """Extract the AEH validator verdict from a replay log."""
    if not replay_file or not os.path.isfile(replay_file):
        return None
    with open(replay_file, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    try:
        data = yaml.safe_load(text)
        if isinstance(data, dict) and data.get("status"):
            return str(data["status"])
    except Exception:
        pass
    for marker in ("BLOCKED_CHANGE_STATE", "BLOCKED_RUNTIME_INTEGRITY", "MERGE_READY",
                   "READY_WITH_WARNINGS"):
        if marker in text:
            return marker
    return "UNKNOWN"


def check_aeh_evidence(work_dir, session_log=None, replay_file=None):
    """Return {"artifacts_present", "aeh_cli_by_agent", "validator_replay", "artifacts"}."""
    artifacts_present = all(
        os.path.isfile(os.path.join(work_dir, prefix, suffix))
        for prefix, suffix in REQUIRED_AEH_FILES)
    change_files = _glob_exists(work_dir, REQUIRED_CHANGE_FILES[0])
    artifacts = []
    for cf in change_files:
        base = os.path.dirname(cf)
        for art in WORKFLOW_ARTIFACTS:
            p = os.path.join(base, art)
            if os.path.isfile(p):
                artifacts.append(os.path.relpath(p, work_dir))
    artifacts_present = artifacts_present and bool(change_files) and bool(artifacts)

    if isinstance(session_log, str):
        session_text = session_log
    elif session_log and os.path.isfile(session_log):
        with open(session_log, "r", encoding="utf-8", errors="ignore") as f:
            session_text = f.read()
    else:
        session_text = ""
    cli_by_agent = ("aeh " in session_text or "aeh." in session_text or "aeh\n" in session_text)

    return {
        "artifacts_present": artifacts_present,
        "aeh_cli_by_agent": cli_by_agent,
        "validator_replay": {"executed": bool(replay_file and os.path.isfile(replay_file)),
                             "verdict": _replay_verdict(replay_file)},
        "artifacts": artifacts,
    }
