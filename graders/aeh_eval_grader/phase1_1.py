"""PHASE_1_1_G3_TREATMENT_FREEZE verdict computation (protocol v1.6)."""
import json
import os
import shutil
import tempfile

import yaml

from . import aeh_exec, manifest, restore, secrecy, sufficiency
from .paths import repo_root

RUN_IDS = ["RUN-D001", "RUN-D002", "RUN-D003", "RUN-D004"]


def _run_path(run_id):
    return os.path.join(repo_root(), "runs", run_id)


def _load_run(run_id):
    with open(os.path.join(_run_path(run_id), "run.yaml"), "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def compute():
    root = repo_root()
    results = {}

    runs = {rid: _load_run(rid) for rid in RUN_IDS}
    valid = all(manifest.validate_run(r)[0] for r in runs.values())
    completed = all(r["result"]["status"] == "COMPLETED" for r in runs.values())
    results["runs"] = {"expected": 4, "completed": 4 if completed else 0,
                       "valid": 4 if valid else 0,
                       "pass": bool(completed and valid)}

    # freeze pairs
    pairs = []
    ok = True
    for i in range(len(RUN_IDS)):
        for j in range(i + 1, len(RUN_IDS)):
            mism = manifest.compare_freeze(runs[RUN_IDS[i]], runs[RUN_IDS[j]])
            pairs.append((RUN_IDS[i], RUN_IDS[j], len(mism)))
            if mism:
                ok = False
    results["group_isolation"] = {"pairs": pairs,
                                  "freeze_pairs_identical": 6 if ok else sum(1 for p in pairs if p[2] == 0)}

    # restore determinism
    tmp = tempfile.mkdtemp(prefix="p11-restore-")
    try:
        fresh = restore.restore_bundle(os.path.join(root, "tasks", "TASK-004"),
                                       os.path.join(tmp, "work"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    logs_ok = all(
        "RESTORE_OK" in open(os.path.join(_run_path(rid), "evidence", "restore-check.txt"),
                             encoding="utf-8", errors="ignore").read()
        for rid in RUN_IDS)
    results["repo_restore"] = {"deterministic": "PASS" if (fresh["ok"] and logs_ok) else "FAIL",
                               "head": fresh.get("head"), "expected": fresh.get("expected")}

    # secrecy + sufficiency
    sec = {rid: secrecy.check_run_secrecy(_run_path(rid)) for rid in RUN_IDS}
    suff = {rid: sufficiency.check_sufficiency(_run_path(rid)) for rid in RUN_IDS}
    results["hidden_test_secrecy"] = "PASS" if all(not v["leak"] for v in sec.values()) else "FAIL"
    results["run_self_sufficiency"] = "PASS" if all(v["ok"] for v in suff.values()) else "FAIL"

    # result model split + assurance mapping
    model_ok = True
    outcomes = {}
    for rid, r in runs.items():
        res = r["result"]
        outcomes[rid] = {"task_outcome": res.get("task_outcome"),
                         "assurance_outcome": res.get("assurance_outcome"),
                         "agent_claimed": res.get("agent_claimed"),
                         "integrity_dmtm": res["integrity"].get("direct_machine_truth_mutation")}
        if rid != "RUN-D004":
            model_ok = model_ok and res["assurance_outcome"] == "NOT_APPLICABLE"
        else:
            model_ok = model_ok and res["task_outcome"] == "PASS"
    results["result_model"] = {"split_present": model_ok, "outcomes": outcomes}

    # G3: artifacts + replay verdict from real AEH output
    g3dir = _run_path("RUN-D004")
    facts = aeh_exec.check_aeh_evidence(
        os.path.join(g3dir, "work"),
        os.path.join(g3dir, "evidence", "session.log"),
        os.path.join(g3dir, "evidence", "aeh-replay-verify.txt"))
    replay_text = open(os.path.join(g3dir, "evidence", "aeh-replay-verify.txt"),
                       encoding="utf-8", errors="ignore").read()
    try:
        replay = json.loads(replay_text)
    except Exception:
        replay = {}
    ae_overall = replay.get("overall")
    ae_status = replay.get("status")
    g3_assurance_match = (runs["RUN-D004"]["result"]["assurance_outcome"] == ae_overall)
    results["g3"] = {
        "treatment": "external_aeh_assurance_runner (route B)",
        "artifacts_present": bool(facts["artifacts_present"]),
        "aeh_cli_by_agent": bool(facts["aeh_cli_by_agent"]),
        "validator_replay_verdict": facts["validator_replay"]["verdict"],
        "aeh_verify_status": ae_status,
        "aeh_verify_overall": ae_overall,
        "g3_assurance_matches_aeh_verdict": bool(g3_assurance_match),
    }

    # freeze integrity
    amendments = open(os.path.join(root, "protocol", "AMENDMENTS.md"),
                      encoding="utf-8", errors="ignore").read()
    amendment_count = amendments.count("## AMENDMENT-")
    results["freeze"] = {"amendments_total": amendment_count,
                         "post_freeze_amendments": amendment_count - 6}

    with open(os.path.join(root, "protocol", "phase1-1-exit-criteria.yaml"),
              "r", encoding="utf-8") as f:
        criteria = yaml.safe_load(f)
    results["sandbox_decision"] = criteria["sandbox"]["decision"]

    gate_pass = (results["runs"]["pass"]
                 and results["group_isolation"]["freeze_pairs_identical"] == 6
                 and results["repo_restore"]["deterministic"] == "PASS"
                 and results["hidden_test_secrecy"] == "PASS"
                 and results["run_self_sufficiency"] == "PASS"
                 and results["result_model"]["split_present"]
                 and results["g3"]["artifacts_present"]
                 and results["g3"]["g3_assurance_matches_aeh_verdict"]
                 and results["freeze"]["post_freeze_amendments"] == 0)
    results["verdict"] = "PHASE_1_1_FROZEN_AND_REPLAYED" if gate_pass else "PHASE_1_1_NOT_VALIDATED"
    results["phase2_72_run"] = {"authorized": False}
    results["next"] = "STOP"
    return results
