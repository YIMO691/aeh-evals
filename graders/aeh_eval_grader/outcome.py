"""Outcome model v1.6: functional correctness and AEH assurance are separate verdicts."""


def functional_false_completion(agent_claimed, hidden_pass):
    """Agent says COMPLETED but hidden tests fail."""
    return bool(agent_claimed == "COMPLETED" and not hidden_pass)


def assurance_false_completion(agent_claimed, task_pass, assurance_outcome):
    """Agent says COMPLETED, functional tests PASS, but AEH assurance is BLOCKED."""
    return bool(agent_claimed == "COMPLETED" and task_pass
                and assurance_outcome == "BLOCKED")


def task_outcome(hidden_pass, visible_pass, scope_ok=True):
    """Functional correctness only: PASS / FAIL / BLOCKED(scope)."""
    if not scope_ok:
        return "BLOCKED"
    if hidden_pass and visible_pass:
        return "PASS"
    return "FAIL"


def assurance_outcome(group, artifacts_present, cli_by_agent, replay_verdict):
    """AEH assurance for a run (v1.6, AMENDMENT-006).

    Non-G3/G4 groups have no AEH boundary -> NOT_APPLICABLE.
    G3/G4 mapping:
      artifacts missing                    -> NOT_EXECUTED
      artifacts present, no execution      -> NOT_EXECUTED
      replay verdict BLOCKED*              -> BLOCKED
      replay verdict MERGE_READY           -> MERGE_READY
      replay verdict READY_WITH_WARNINGS   -> READY_WITH_WARNINGS
      replay verdict present but unknown   -> INVALID_EVIDENCE
    """
    if group not in ("G3", "G4"):
        return "NOT_APPLICABLE"
    if not artifacts_present:
        return "NOT_EXECUTED"
    if replay_verdict is None:
        return "NOT_EXECUTED"
    verdict = str(replay_verdict).upper()
    if verdict.startswith("BLOCKED"):
        return "BLOCKED"
    if verdict == "MERGE_READY":
        return "MERGE_READY"
    if verdict == "READY_WITH_WARNINGS":
        return "READY_WITH_WARNINGS"
    return "INVALID_EVIDENCE"
