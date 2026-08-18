"""Command-line entry points for the deterministic graders."""
import argparse
import os
import sys

import yaml

from .aeh_eval_grader import aeh_exec as aeh_exec_mod
from .aeh_eval_grader import attack as attack_mod
from .aeh_eval_grader import diff as diff_mod
from .aeh_eval_grader import manifest as manifest_mod
from .aeh_eval_grader import outcome as outcome_mod
from .aeh_eval_grader import phase1 as phase1_mod
from .aeh_eval_grader import report as report_mod
from .aeh_eval_grader import restore as restore_mod
from .aeh_eval_grader import secrecy as secrecy_mod
from .aeh_eval_grader import sufficiency as sufficiency_mod


def main(argv=None):
    parser = argparse.ArgumentParser(prog="grader")
    sub = parser.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("validate", help="validate a run.yaml against the frozen schema")
    v.add_argument("--run", required=True, help="path to run.yaml")

    d = sub.add_parser("diff", help="check changed paths against a task allowed_scope")
    d.add_argument("--changed", required=True, help="comma separated changed paths")
    d.add_argument("--scope-file", required=True, help="path to task.yaml")

    a = sub.add_parser("attack", help="map observed signals to an attack verdict")
    a.add_argument("--attack", required=True, choices=attack_mod.ATTACK_IDS)
    a.add_argument("--signals", default="", help="comma separated observed signals")
    a.add_argument("--group", default="G3", help="run group G0-G4")

    m = sub.add_parser("matrix", help="aggregate runs/ into the evidence matrix CSV")
    m.add_argument("--out", default=None, help="optional output file")

    rc = sub.add_parser("restore-check", help="restore task bundle and verify frozen SHA")
    rc.add_argument("--task", required=True, help="task directory")
    rc.add_argument("--workdir", required=True, help="empty target workdir")

    rv = sub.add_parser("restore-verify", help="verify an existing workdir SHA/clean state")
    rv.add_argument("--workdir", required=True)
    rv.add_argument("--sha", required=True)

    fc = sub.add_parser("freeze-compare", help="compare frozen fields of two run manifests")
    fc.add_argument("--run-a", required=True)
    fc.add_argument("--run-b", required=True)

    sc = sub.add_parser("secrecy", help="scan a run directory for hidden-test leakage")
    sc.add_argument("--run-dir", required=True)

    oc = sub.add_parser("outcome", help="compute false_completion and deterministic outcome")
    oc.add_argument("--agent-claimed", required=True,
                    choices=["COMPLETED", "INCOMPLETE", "UNKNOWN", "NOT_RECORDED"])
    oc.add_argument("--hidden-pass", required=True, choices=["true", "false"])
    oc.add_argument("--visible-pass", default="true", choices=["true", "false"])
    oc.add_argument("--scope-ok", default="true", choices=["true", "false"])

    ae = sub.add_parser("aeh-evidence", help="check G3 worktree for real AEH artifacts")
    ae.add_argument("--workdir", required=True)
    ae.add_argument("--session-log", default=None)
    ae.add_argument("--replay", default=None, help="operator AEH validator replay log")

    pv = sub.add_parser("phase1-verdict", help="compute PHASE_1_DRY_RUN verdict")
    pv.add_argument("--out", required=True, help="output verdict yaml path")

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

    if args.cmd == "outcome":
        hidden = args.hidden_pass == "true"
        visible = args.visible_pass == "true"
        scope = args.scope_ok == "true"
        print("false_completion=" + str(outcome_mod.false_completion(args.agent_claimed, hidden)).lower())
        print("outcome=" + outcome_mod.outcome(args.agent_claimed, hidden, scope, visible))
        return 0

    if args.cmd == "aeh-evidence":
        result = aeh_exec_mod.check_aeh_evidence(args.workdir, args.session_log, args.replay)
        print(result["detail"])
        for key, value in result["checks"].items():
            print("  %s=%s" % (key, value))
        for art in result["artifacts"]:
            print("  artifact: " + art)
        return 0 if result["ok"] else 1

    if args.cmd == "phase1-verdict":
        result = phase1_mod.compute()
        with open(args.out, "w", encoding="utf-8") as f:
            yaml.safe_dump(result, f, sort_keys=True, allow_unicode=True)
        print("VERDICT=" + result["verdict"])
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
