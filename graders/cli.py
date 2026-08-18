"""Command-line entry points for the deterministic graders."""
import argparse
import os
import sys

import yaml

from .aeh_eval_grader import attack as attack_mod
from .aeh_eval_grader import diff as diff_mod
from .aeh_eval_grader import manifest as manifest_mod
from .aeh_eval_grader import report as report_mod


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

    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
