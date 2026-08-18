"""Aggregate runs/ into the evidence matrix and metrics CSVs."""
import csv
import io
import os

import yaml

from .paths import repo_root

MATRIX_COLUMNS = ["task_id", "G0", "G1", "G2", "G3", "G4", "aeh_gain"]


def load_runs():
    """Load every runs/RUN-*/run.yaml that exists. Returns list of dicts."""
    runs_dir = os.path.join(repo_root(), "runs")
    found = []
    if not os.path.isdir(runs_dir):
        return found
    for name in sorted(os.listdir(runs_dir)):
        if not name.startswith("RUN-"):
            continue
        path = os.path.join(runs_dir, name, "run.yaml")
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                found.append((name, yaml.safe_load(f)))
    return found


def evidence_matrix(runs=None):
    """Build a per-task x per-group verdict matrix CSV string."""
    runs = load_runs() if runs is None else runs
    table = {}
    for name, run in runs:
        if run.get("result", {}).get("status") != "COMPLETED":
            continue
        task = run.get("task_id")
        group = run.get("group")
        outcome = run.get("result", {}).get("outcome", "UNKNOWN")
        table.setdefault(task, {})[group] = outcome
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=MATRIX_COLUMNS)
    writer.writeheader()
    for task in sorted(table):
        row = {"task_id": task}
        row.update({g: table[task].get(g, "") for g in ("G0", "G1", "G2", "G3", "G4")})
        row["aeh_gain"] = ""
        writer.writerow(row)
    return out.getvalue()
