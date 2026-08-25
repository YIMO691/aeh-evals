"""Command-line entry points for the deterministic graders (v1.6)."""
import argparse
import os
import sys

import yaml

from .aeh_eval_grader import aeh_exec as aeh_exec_mod
from .aeh_eval_grader import attack as attack_mod
from .aeh_eval_grader import diff as diff_mod
from .aeh_eval_grader import manifest as manifest_mod
from .aeh_eval_grader import outcome as outcome_mod
from .aeh_eval_grader import phase1_1 as phase1_1_mod
from .aeh_eval_grader import phase2_readiness as phase2_readiness_mod
from .aeh_eval_grader import report as report_mod
from .aeh_eval_grader import restore as restore_mod
from .aeh_eval_grader import secrecy as secrecy_mod
from .aeh_eval_grader import sufficiency as sufficiency_mod


def main(argv=None):
    parser = argparse.ArgumentParser(prog="grader")
    sub = parser.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("validate", help="validate a run.yaml against the frozen schema")
    v.add_argument("--run", required=True)

    d = sub.add_parser("diff", help="check changed paths against a task allowed_scope")
    d.add_argument("--changed", required=True)
    d.add_argument("--scope-file", required=True)

    a = sub.add_parser("attack", help="map observed signals to an attack verdict")
    a.add_argument("--attack", required=True, choices=attack_mod.ATTACK_IDS)
    a.add_argument("--signals", default="")
    a.add_argument("--group", default="G3")

    m = sub.add_parser("matrix", help="aggregate runs/ into the evidence matrix CSV")
    m.add_argument("--out", default=None)

    rc = sub.add_parser("restore-check", help="restore task bundle and verify frozen SHA")
    rc.add_argument("--task", required=True)
    rc.add_argument("--workdir", required=True)

    rv = sub.add_parser("restore-verify", help="verify workdir SHA/clean state")
    rv.add_argument("--workdir", required=True)
    rv.add_argument("--sha", required=True)

    fc = sub.add_parser("freeze-compare", help="compare frozen fields of two run manifests")
    fc.add_argument("--run-a", required=True)
    fc.add_argument("--run-b", required=True)

    sc = sub.add_parser("secrecy", help="scan run dir for hidden-test leakage")
    sc.add_argument("--run-dir", required=True)

    to = sub.add_parser("task-outcome", help="functional task_outcome + functional false completion")
    to.add_argument("--agent-claimed", required=True,
                    choices=["COMPLETED", "INCOMPLETE", "UNKNOWN", "NOT_RECORDED"])
    to.add_argument("--hidden-pass", required=True, choices=["true", "false"])
    to.add_argument("--visible-pass", default="true", choices=["true", "false"])
    to.add_argument("--scope-ok", default="true", choices=["true", "false"])

    ao = sub.add_parser("assurance", help="assurance_outcome + assurance false completion")
    ao.add_argument("--group", required=True, choices=["G0", "G1", "G2", "G3", "G4"])
    ao.add_argument("--artifacts", required=True, choices=["true", "false"])
    ao.add_argument("--cli", required=True, choices=["true", "false"])
    ao.add_argument("--replay-verdict", default=None)
    ao.add_argument("--agent-claimed", default="NOT_RECORDED",
                    choices=["COMPLETED", "INCOMPLETE", "UNKNOWN", "NOT_RECORDED"])
    ao.add_argument("--task-pass", default="true", choices=["true", "false"])

    ae = sub.add_parser("aeh-evidence", help="report AEH evidence facts for a G3 worktree")
    ae.add_argument("--workdir", required=True)
    ae.add_argument("--session-log", default=None)
    ae.add_argument("--replay", default=None)

    p1 = sub.add_parser("phase1-1-verdict", help="compute PHASE_1_1 verdict")
    p1.add_argument("--out", required=True)

    sub.add_parser("phase2-readiness", help="validate the Phase 2 v1.7 candidate package")
    sub.add_parser("phase2-input-manifest", help="render the canonical Phase 2 v1.7 input manifest")
    from .aeh_eval_grader import phase2_v18_readiness as phase2_v18_readiness_mod
    sub.add_parser("phase2-v1.8-readiness", help="validate the corrected Phase 2 v1.8 candidate package")
    sub.add_parser("phase2-v1.8-input-manifest", help="render the canonical Phase 2 v1.8 input manifest")
    from .aeh_eval_grader import phase2_v19_readiness as phase2_v19_readiness_mod
    sub.add_parser("phase2-v1.9-readiness", help="validate the corrected Phase 2 v1.9 candidate package")
    sub.add_parser("phase2-v1.9-input-manifest", help="render the canonical Phase 2 v1.9 input manifest")
    from .aeh_eval_grader import phase2_v110_readiness as phase2_v110_readiness_mod
    sub.add_parser("phase2-v1.10-readiness", help="validate the Phase 2 v1.10 UTF-8 capture candidate")
    sub.add_parser("phase2-v1.10-input-manifest", help="render the canonical Phase 2 v1.10 input manifest")

    sf = sub.add_parser("sufficiency", help="check run bundle required files")
    sf.add_argument("--run-dir", required=True)

    args = parser.parse_args(argv)

    if args.cmd == "validate":
        with open(args.run, "r", encoding="utf-8") as f:
            run = yaml.safe_load(f)
        ok, errors = manifest_mod.validate_run(run)
        if ok:
            print("VALID")
            return 0
        print("INVALID_RUN")
        for e in errors:
            print("  - " + e)
        return 1

    if args.cmd == "diff":
        with open(args.scope_file, "r", encoding="utf-8") as f:
            task = yaml.safe_load(f)
        changed = [p.strip() for p in args.changed.split(",") if p.strip()]
        violations = diff_mod.scope_violations(changed, task.get("allowed_scope") or [])
        if violations:
            print("SCOPE_VIOLATION")
            for path in violations:
                print("  - " + path)
            return 1
        print("SCOPE_OK")
        return 0

    if args.cmd == "attack":
        signals = [s.strip() for s in args.signals.split(",") if s.strip()]
        print(attack_mod.verdict(args.attack, signals, args.group))
        return 0

    if args.cmd == "matrix":
        csv_text = report_mod.evidence_matrix()
        if args.out:
            with open(args.out, "w", encoding="utf-8", newline="") as f:
                f.write(csv_text)
        sys.stdout.write(csv_text)
        return 0

    if args.cmd == "restore-check":
        result = restore_mod.restore_bundle(args.task, args.workdir)
        print(result["detail"])
        print("head=" + str(result["head"]))
        print("expected=" + str(result["expected"]))
        print("dirty='" + str(result["dirty"]) + "'")
        return 0 if result["ok"] else 1

    if args.cmd == "restore-verify":
        result = restore_mod.verify_restore(args.workdir, args.sha)
        print(result["detail"])
        print("head=" + str(result["head"]))
        print("dirty='" + str(result["dirty"]) + "'")
        return 0 if result["ok"] else 1

    if args.cmd == "freeze-compare":
        with open(args.run_a, "r", encoding="utf-8") as f:
            run_a = yaml.safe_load(f)
        with open(args.run_b, "r", encoding="utf-8") as f:
            run_b = yaml.safe_load(f)
        mismatches = manifest_mod.compare_freeze(run_a, run_b)
        if mismatches:
            print("MISMATCHES=" + str(len(mismatches)))
            for key, va, vb in mismatches:
                print("  - %s: %r != %r" % (key, va, vb))
            return 1
        print("FREEZE_IDENTICAL")
        return 0

    if args.cmd == "secrecy":
        result = secrecy_mod.check_run_secrecy(args.run_dir)
        if result["leak"]:
            print("LEAK")
            for hit in result["hits"]:
                print("  - " + hit)
            return 1
        print("SECRECY_OK")
        return 0

    if args.cmd == "task-outcome":
        hidden = args.hidden_pass == "true"
        visible = args.visible_pass == "true"
        scope = args.scope_ok == "true"
        print("functional_false_completion="
              + str(outcome_mod.functional_false_completion(args.agent_claimed, hidden)).lower())
        print("task_outcome=" + outcome_mod.task_outcome(hidden, visible, scope))
        return 0

    if args.cmd == "assurance":
        artifacts = args.artifacts == "true"
        cli = args.cli == "true"
        assurance = outcome_mod.assurance_outcome(args.group, artifacts, cli, args.replay_verdict)
        task_pass = args.task_pass == "true"
        print("assurance_outcome=" + assurance)
        print("assurance_false_completion="
              + str(outcome_mod.assurance_false_completion(args.agent_claimed, task_pass, assurance)).lower())
        return 0

    if args.cmd == "aeh-evidence":
        result = aeh_exec_mod.check_aeh_evidence(args.workdir, args.session_log, args.replay)
        print("artifacts_present=" + str(result["artifacts_present"]).lower())
        print("aeh_cli_by_agent=" + str(result["aeh_cli_by_agent"]).lower())
        print("validator_replay_executed=" + str(result["validator_replay"]["executed"]).lower())
        print("validator_replay_status=" + str(result["validator_replay"]["status"]))
        print("validator_replay_overall=" + str(result["validator_replay"]["overall"]))
        print("validator_replay_verdict=" + str(result["validator_replay"]["verdict"]))
        for art in result["artifacts"]:
            print("  artifact: " + art)
        return 0

    if args.cmd == "phase1-1-verdict":
        result = phase1_1_mod.compute()
        with open(args.out, "w", encoding="utf-8") as f:
            yaml.safe_dump(result, f, sort_keys=True, allow_unicode=True)
        print("VERDICT=" + result["verdict"])
        return 0

    if args.cmd == "phase2-readiness":
        result = phase2_readiness_mod.compute()
        print(result["verdict"])
        print("planned_blocks=" + str(result["planned_blocks"]))
        print("planned_runs=" + str(result["planned_runs"]))
        print("phase2_authorized=" + str(result["phase2_authorized"]).lower())
        for error in result["errors"]:
            print("  - " + error)
        return 0 if not result["errors"] else 1

    if args.cmd == "phase2-input-manifest":
        sys.stdout.write(phase2_readiness_mod.render_input_manifest())
        return 0

    if args.cmd == "phase2-v1.8-readiness":
        result = phase2_v18_readiness_mod.compute()
        print(result["verdict"])
        print("planned_blocks=" + str(result["planned_blocks"]))
        print("planned_runs=" + str(result["planned_runs"]))
        print("phase2_authorized=" + str(result["phase2_authorized"]).lower())
        for error in result["errors"]:
            print("  - " + error)
        return 0 if not result["errors"] else 1

    if args.cmd == "phase2-v1.8-input-manifest":
        sys.stdout.write(phase2_v18_readiness_mod.render_input_manifest())
        return 0

    if args.cmd == "phase2-v1.9-readiness":
        result = phase2_v19_readiness_mod.compute()
        print(result["verdict"])
        print("planned_blocks=" + str(result["planned_blocks"]))
        print("planned_runs=" + str(result["planned_runs"]))
        print("phase2_authorized=" + str(result["phase2_authorized"]).lower())
        for error in result["errors"]:
            print("  - " + error)
        return 0 if not result["errors"] else 1

    if args.cmd == "phase2-v1.9-input-manifest":
        sys.stdout.write(phase2_v19_readiness_mod.render_input_manifest())
        return 0

    if args.cmd == "phase2-v1.10-readiness":
        result = phase2_v110_readiness_mod.compute()
        print(result["verdict"])
        print("planned_blocks=" + str(result["planned_blocks"]))
        print("planned_runs=" + str(result["planned_runs"]))
        print("phase2_authorized=" + str(result["phase2_authorized"]).lower())
        for error in result["errors"]:
            print("  - " + error)
        return 0 if not result["errors"] else 1

    if args.cmd == "phase2-v1.10-input-manifest":
        sys.stdout.write(phase2_v110_readiness_mod.render_input_manifest())
        return 0

    if args.cmd == "sufficiency":
        result = sufficiency_mod.check_sufficiency(args.run_dir)
        if result["ok"]:
            print("SELF_SUFFICIENT")
            return 0
        print("MISSING")
        for path in result["missing"]:
            print("  - " + path)
        return 1

    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
