"""Run manifest validation and frozen-environment comparison."""
import json
import os

import jsonschema
import yaml

from .paths import repo_root

# AMENDMENT-002: config_sha256 encodes the per-group environment and is therefore
# NOT compared across groups. Cross-group equality covers exactly the invariant
# fields: repository, agent, environment, task prompt.
FREEZE_FIELDS = [
    ("repository", "commit_sha"),
    ("agent", "vendor"),
    ("agent", "product"),
    ("agent", "version"),
    ("agent", "model"),
    ("environment", "os"),
    ("environment", "python_or_dotnet"),
    ("environment", "sandbox"),
    ("environment", "network"),
    ("environment", "timeout"),
    ("input", "task_prompt_sha256"),
]


def load_run_schema():
    path = os.path.join(repo_root(), "protocol", "run-manifest.schema.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_run(run):
    """Return (ok, [error messages])."""
    errors = []
    try:
        jsonschema.validate(run, load_run_schema())
    except jsonschema.ValidationError as exc:
        return False, [exc.message]
    return True, errors


def freeze_values(run):
    """Extract the frozen environment fields from a run manifest."""
    out = {}
    for section, key in FREEZE_FIELDS:
        out[section + "." + key] = run.get(section, {}).get(key)
    return out


def compare_freeze(run_a, run_b):
    """Compare frozen fields between two runs. Return list of mismatches."""
    a = freeze_values(run_a)
    b = freeze_values(run_b)
    mismatches = []
    for key in a:
        if a[key] != b.get(key):
            mismatches.append((key, a[key], b.get(key)))
    return mismatches
