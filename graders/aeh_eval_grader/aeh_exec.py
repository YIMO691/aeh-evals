"""G3 evidence check: AEH must actually execute, not merely be mentioned."""
import os

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


def check_aeh_evidence(work_dir, session_log=None, replay_file=None):
    """Check that a G3 worktree contains real AEH machine artifacts and that
    the AEH CLI actually executed (AMENDMENT-005):

    - either the executing agent invoked `aeh` commands (session log), or
    - the operator replayed the AEH validators afterwards and recorded the
      verdict (replay file). AEH enforcement is demonstrated by the replay
      verdict regardless of agent compliance.
    """
    checks = {}
    for prefix, suffix in REQUIRED_AEH_FILES:
        checks["aeh_manifest"] = os.path.isfile(os.path.join(work_dir, prefix, suffix))
    change_files = _glob_exists(work_dir, REQUIRED_CHANGE_FILES[0])
    checks["change_yaml"] = bool(change_files)
    artifacts = []
    for cf in change_files:
        base = os.path.dirname(cf)
        for art in WORKFLOW_ARTIFACTS:
            p = os.path.join(base, art)
            if os.path.isfile(p):
                artifacts.append(os.path.relpath(p, work_dir))
    checks["workflow_artifacts"] = bool(artifacts)

    def _log_text(src):
        if src is None:
            return ""
        if isinstance(src, str):
            return src
        with open(src, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    session_text = _log_text(session_log)
    checks["aeh_cli_invoked_by_agent"] = ("aeh " in session_text
                                          or "aeh." in session_text
                                          or "aeh\n" in session_text)
    replay_text = ""
    if replay_file and os.path.isfile(replay_file):
        with open(replay_file, "r", encoding="utf-8", errors="ignore") as f:
            replay_text = f.read()
    checks["validator_replay"] = bool(
        replay_file and os.path.isfile(replay_file)
        and (("BLOCKED_CHANGE_STATE" in replay_text)
             or ("aeh" in replay_text and "overall" in replay_text)))
    checks["actual_aeh_execution"] = (checks["aeh_cli_invoked_by_agent"]
                                      or checks["validator_replay"])
    ok = (checks["aeh_manifest"] and checks["change_yaml"]
          and checks["workflow_artifacts"] and checks["actual_aeh_execution"])
    return {"ok": ok, "checks": checks,
            "detail": "AEH_EVIDENCE_OK" if ok else "AEH_EVIDENCE_MISSING",
            "artifacts": artifacts}
