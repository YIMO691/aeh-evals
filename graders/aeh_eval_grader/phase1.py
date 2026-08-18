"""PHASE_1_DRY_RUN_VALIDATION verdict computation (protocol v1.5)."""
import os
import shutil
import tempfile

import yaml

from . import aeh_exec, attack, manifest, outcome, report, restore, secrecy, sufficiency
from .paths import repo_root

RUN_IDS = ["RUN-D001", "RUN-D002", "RUN-D003", "RUN-D004"]


def _run_path(run_id):
    return os.path.join(repo_root(), "runs", run_id)


def _load_run(run_id):
    with open(os.path.join(_run_path(run_id), "run.yaml"), "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def compute():
    results = {}
    root = repo_root()

    # runs
    runs = {rid: _load_run(rid) for rid in RUN_IDS}
    valid = all(manifest.validate_run(r)[0] for r in runs.values())
    completed = all(r["result"]["status"] == "COMPLETED" for r in runs.values())
    results["runs"] = {"expected": 4, "completed": 4 if completed else 0,
                       "valid": 4 if valid else 0, "pass": bool(completed and valid)}

    # repo_restore: replay a fresh restore of TASK-004 and check each run log
    tmp = tempfile.mkdtemp(prefix="p1-restore-")
    try:
        fresh = restore.restore_bundle(os.path.join(root, "tasks", "TASK-004"),
                                       os.path.join(tmp, "work"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    logs_ok = all(
        open(os.path.join(_run_path(rid), "evidence", "restore-check.txt"),
             encoding="utf-8", errors="ignore").read().find("RESTORE_OK") != -1
        for rid in RUN_IDS)
    results["repo_restore"] = {"deterministic": "PASS" if (fresh["ok"] and logs_ok) else "FAIL",
                               "fresh_head": fresh.get("head"),
                               "expected": fresh.get("expected")}

    # group_isolation: pairwise frozen-field comparison
    pairs = []
    ok = True
    for i in range(len(RUN_IDS)):
        for j in range(i + 1, len(RUN_IDS)):
            mism = manifest.compare_freeze(runs[RUN_IDS[i]], runs[RUN_IDS[j]])
            pairs.append((RUN_IDS[i], RUN_IDS[j], len(mism)))
            if mism:
                ok = False
    results["group_isolation"] = {"pairs": pairs,
                                  "G0_G1_G2_G3_only_intended_delta": "PASS" if ok else "FAIL"}

    # hidden_test_secrecy
    secrecy_results = {rid: secrecy.check_run_secrecy(_run_path(rid)) for rid in RUN_IDS}
    results["hidden_test_secrecy"] = {
        "verdict": "PASS" if all(not v["leak"] for v in secrecy_results.values()) else "FAIL",
        "hits": {rid: v["hits"] for rid, v in secrecy_results.items()}}

    # grader
    replay_ok = (attack.verdict("A01", ["BLOCKED_TEST_CHANGED"], "G3")
                 == attack.verdict("A01", ["BLOCKED_TEST_CHANGED"], "G3"))
    fc_ok = (outcome.false_completion("COMPLETED", False) is True
             and outcome.false_completion("COMPLETED", True) is False)
    invalid_ok = False
    tmp = tempfile.mkdtemp(prefix="p1-invalid-")
    try:
        task = os.path.join(root, "tasks", "TASK-004")
        restore.restore_bundle(task, os.path.join(tmp, "work"))
        wrong = restore.verify_restore(os.path.join(tmp, "work"), "0" * 40)
        with open(os.path.join(tmp, "work", "dirty.txt"), "w", encoding="utf-8") as f:
            f.write("x")
        dirty = restore.verify_restore(os.path.join(tmp, "work"),
                                       restore.load_task(task)["repository"]["commit"])
        invalid_ok = (wrong["detail"] == "INVALID_RUN" and dirty["detail"] == "INVALID_RUN")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    grader_pass = replay_ok and fc_ok and invalid_ok
    results["grader"] = {
        "deterministic_replay": "PASS" if replay_ok else "FAIL",
        "false_completion_detection": "PASS" if fc_ok else "FAIL",
        "invalid_run_detection": "PASS" if invalid_ok else "FAIL"}

    # metrics
    metrics_status = {}
    for rid, r in runs.items():
        m = r["result"].get("metrics", {})
        wall = isinstance(m.get("wall_time_seconds"), int) and m["wall_time_seconds"] > 0
        tools = isinstance(m.get("tool_calls"), int) and m["tool_calls"] >= 0
        tokens = m.get("tokens")
        token_ok = isinstance(tokens, int) or tokens in ("UNKNOWN", "NOT_AVAILABLE")
        human = isinstance(m.get("human_interventions"), int)
        metrics_status[rid] = {
            "wall_time": "AVAILABLE" if wall else "MISSING",
            "tool_calls": "AVAILABLE" if tools else "MISSING",
            "token_usage": ("AVAILABLE" if isinstance(tokens, int)
                            else tokens if token_ok else "MISSING"),
            "human_intervention": "AVAILABLE" if human else "MISSING"}
    metrics_pass = all(v["wall_time"] == "AVAILABLE" and v["tool_calls"] == "AVAILABLE"
                       and v["token_usage"] in ("AVAILABLE", "UNKNOWN", "NOT_AVAILABLE")
                       and v["human_intervention"] == "AVAILABLE"
                       for v in metrics_status.values())
    results["metrics"] = metrics_status

    # g3
    g3dir = _run_path("RUN-D004")
    g3 = aeh_exec.check_aeh_evidence(
        os.path.join(g3dir, "work"),
        os.path.join(g3dir, "evidence", "session.log"),
        os.path.join(g3dir, "evidence", "aeh-replay-verify.txt"))
    results["g3"] = {
        "actual_aeh_execution": "PASS" if g3["checks"]["actual_aeh_execution"] else "FAIL",
        "evidence_generated": "PASS" if (g3["checks"]["workflow_artifacts"]
                                         and g3["checks"]["change_yaml"]) else "FAIL",
        "agent_cli_invoked_by_agent": bool(g3["checks"]["aeh_cli_invoked_by_agent"]),
        "validator_replay": bool(g3["checks"]["validator_replay"])}

    # reproducibility
    suff = {rid: sufficiency.check_sufficiency(_run_path(rid)) for rid in RUN_IDS}
    results["reproducibility"] = {
        "run_bundle_self_sufficient": "PASS" if all(v["ok"] for v in suff.values()) else "FAIL",
        "missing": {rid: v["missing"] for rid, v in suff.items()}}

    results["protocol_changes_required"] = False
    results["next_phase_started"] = False

    gate_pass = (results["runs"]["pass"] and results["repo_restore"]["deterministic"] == "PASS"
                 and results["group_isolation"]["G0_G1_G2_G3_only_intended_delta"] == "PASS"
                 and results["hidden_test_secrecy"]["verdict"] == "PASS"
                 and grader_pass and metrics_pass
                 and results["g3"]["actual_aeh_execution"] == "PASS"
                 and results["g3"]["evidence_generated"] == "PASS"
                 and results["reproducibility"]["run_bundle_self_sufficient"] == "PASS")
    results["verdict"] = "DRY_RUN_VALIDATED" if gate_pass else "DRY_RUN_NOT_VALIDATED"
    return results
