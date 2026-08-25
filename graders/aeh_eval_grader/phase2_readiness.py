"""Deterministic validation for the Phase 2 v1.7 readiness package."""
import hashlib
import os

import yaml

from .paths import repo_root


PROTOCOL_VERSION = "1.7"
EXPECTED_GROUPS = ["G0", "G1", "G2", "G3"]
EXPECTED_TASKS = ["TASK-%03d" % number for number in range(1, 7)]
EXPECTED_REPETITIONS = [1, 2, 3]
EXPECTED_AEH = {
    "version": "0.2.0",
    "tag": "v0.2.0",
    "commit": "a914f83b852dc57be946c995f2dc4ec58ac7d208",
    "wheel_name": "adaptive_engineering_harness-0.2.0-py3-none-any.whl",
    "wheel_size": 121717,
    "wheel_sha256": "8fc11f9b42cd90fb4e4d1b64380e429d9ad19d80cacfc76396c0b46f59b3ed19",
}
FIXED_INPUT_PATHS = [
    "protocol/PROTOCOL.md",
    "protocol/FREEZE-v1.6.md",
    "protocol/hypotheses.yaml",
    "protocol/metrics.yaml",
    "protocol/decision-gates.yaml",
    "protocol/run-manifest.schema.json",
    "protocol/task.schema.json",
    "protocol/attack.schema.json",
    "protocol/phase2-v1.7/AMENDMENT-007.md",
    "protocol/phase2-v1.7/SCHEDULE.yaml",
    "environments/G0.yaml",
    "environments/G1.yaml",
    "environments/G2.yaml",
    "environments/G3.yaml",
    "environments/G1-assets/AGENTS.md",
    "environments/G1-assets/context/conventions.md",
    "environments/PHASE_2_RUNBOOK-v1.7.md",
    "graders/cli.py",
]


def _digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sha256_file(path):
    with open(path, "rb") as stream:
        content = stream.read()
    # Git checkouts may materialize CRLF on Windows. Protocol text digests are
    # canonical LF digests; binary bundles remain byte-exact.
    if b"\x00" not in content:
        content = content.replace(b"\r\n", b"\n")
    return hashlib.sha256(content).hexdigest()


def _load(relative_path):
    with open(os.path.join(repo_root(), *relative_path.split("/")), "r", encoding="utf-8") as stream:
        return yaml.safe_load(stream)


def expected_input_paths():
    root = repo_root()
    paths = list(FIXED_INPUT_PATHS)
    grader_dir = os.path.join(root, "graders", "aeh_eval_grader")
    paths.extend(
        "graders/aeh_eval_grader/" + name
        for name in os.listdir(grader_dir)
        if name.endswith(".py")
    )
    for task_id in EXPECTED_TASKS:
        prefix = "tasks/%s/" % task_id
        paths.extend([prefix + "task.yaml", prefix + "repo-src.bundle"])
        hidden_dir = os.path.join(root, *prefix.split("/"), "hidden-tests")
        paths.extend(
            prefix + "hidden-tests/" + name
            for name in os.listdir(hidden_dir)
            if name.startswith("test_") and name.endswith(".py")
        )
        inputs_dir = os.path.join(root, *prefix.split("/"), "aeh-inputs")
        for directory, _, names in os.walk(inputs_dir):
            for name in names:
                absolute = os.path.join(directory, name)
                paths.append(os.path.relpath(absolute, root).replace("\\", "/"))
    return sorted(paths)


def render_input_manifest():
    lines = []
    for path in expected_input_paths():
        absolute = os.path.join(repo_root(), *path.split("/"))
        lines.append("%s  %s" % (_sha256_file(absolute), path))
    return "\n".join(lines) + "\n"


def expected_blocks(seed):
    blocks = []
    for task_id in EXPECTED_TASKS:
        for repetition in EXPECTED_REPETITIONS:
            block_key = "%s|%s|%s" % (seed, task_id, repetition)
            groups = sorted(EXPECTED_GROUPS, key=lambda group: _digest(block_key + "|" + group))
            blocks.append({
                "task_id": task_id,
                "repetition": repetition,
                "groups": groups,
                "_sort": _digest(block_key),
            })
    blocks.sort(key=lambda block: block["_sort"])
    for block in blocks:
        del block["_sort"]
    return blocks


def validate_schedule(schedule):
    errors = []
    if str(schedule.get("protocol_version")) != PROTOCOL_VERSION:
        errors.append("schedule.protocol_version must be 1.7")
    seed = schedule.get("seed")
    blocks = schedule.get("blocks") or []
    expected = expected_blocks(seed or "")
    if blocks != expected:
        errors.append("schedule blocks do not match the deterministic hash-derived order")
    combinations = {(block.get("task_id"), block.get("repetition")) for block in blocks}
    if len(blocks) != 18 or len(combinations) != 18:
        errors.append("schedule must contain 18 unique task/repetition blocks")
    if sum(len(block.get("groups") or []) for block in blocks) != 72:
        errors.append("schedule must expand to exactly 72 runs")
    return errors


def validate_baseline(baseline):
    errors = []
    if str(baseline.get("protocol_version")) != PROTOCOL_VERSION:
        errors.append("baseline.protocol_version must be 1.7")
    if baseline.get("status") != "READY_FOR_PREFLIGHT":
        errors.append("baseline status must be READY_FOR_PREFLIGHT")
    if baseline.get("phase2_72_run", {}).get("authorized") is not False:
        errors.append("Phase 2 must remain unauthorized")
    if baseline.get("attack_runs", {}).get("authorized") is not False:
        errors.append("attack runs must remain unauthorized")

    treatment = baseline.get("aeh_treatment", {})
    wheel = treatment.get("wheel", {})
    observed = {
        "version": str(treatment.get("version")),
        "tag": treatment.get("tag"),
        "commit": treatment.get("commit"),
        "wheel_name": wheel.get("name"),
        "wheel_size": wheel.get("size_bytes"),
        "wheel_sha256": wheel.get("sha256"),
    }
    if observed != EXPECTED_AEH:
        errors.append("AEH treatment does not match the reviewed v0.2.0 release")

    historical = baseline.get("historical_freeze", {})
    if historical.get("rewrite_allowed") is not False:
        errors.append("historical v1.6 freeze must be immutable")
    for item in [historical]:
        relative_path = item.get("path")
        expected_hash = item.get("sha256")
        if not relative_path or not expected_hash:
            errors.append("pinned input is missing path or sha256")
            continue
        absolute_path = os.path.join(repo_root(), *relative_path.split("/"))
        if not os.path.isfile(absolute_path):
            errors.append("pinned input missing: " + relative_path)
        elif _sha256_file(absolute_path) != expected_hash:
            errors.append("pinned input digest mismatch: " + relative_path)
    errors.extend(validate_input_manifest(baseline.get("input_manifest") or {}))
    return errors


def validate_input_manifest(manifest_ref):
    errors = []
    relative_path = manifest_ref.get("path")
    expected_hash = manifest_ref.get("sha256")
    expected_entries = manifest_ref.get("entries")
    if not relative_path or not expected_hash:
        return ["input manifest reference is incomplete"]
    absolute_path = os.path.join(repo_root(), *relative_path.split("/"))
    if not os.path.isfile(absolute_path):
        return ["input manifest is missing: " + relative_path]
    if _sha256_file(absolute_path) != expected_hash:
        errors.append("input manifest digest mismatch")

    entries = []
    with open(absolute_path, "r", encoding="utf-8") as stream:
        for number, raw_line in enumerate(stream, start=1):
            line = raw_line.strip()
            if not line:
                continue
            parts = line.split(None, 1)
            if len(parts) != 2 or len(parts[0]) != 64:
                errors.append("invalid input manifest line %d" % number)
                continue
            entries.append((parts[0], parts[1]))
    if len(entries) != expected_entries:
        errors.append("input manifest entry count mismatch")
    paths = [path for _, path in entries]
    if len(paths) != len(set(paths)):
        errors.append("input manifest contains duplicate paths")
    if paths != expected_input_paths():
        errors.append("input manifest path set/order does not match the v1.7 contract")
    for expected_digest, path in entries:
        full_path = os.path.join(repo_root(), *path.split("/"))
        if not os.path.isfile(full_path):
            errors.append("input missing: " + path)
        elif _sha256_file(full_path) != expected_digest:
            errors.append("input digest mismatch: " + path)

    for task_id in EXPECTED_TASKS:
        prefix = "tasks/%s/aeh-inputs/" % task_id
        required = {
            prefix + "reqs.yaml",
            prefix + "plan.yaml",
            prefix + "scope-v1.7.yaml",
        }
        if not required.issubset(set(paths)):
            errors.append("AEH inputs incomplete for " + task_id)
        if len([path for path in paths if path.startswith(prefix + "test-src/")]) != 1:
            errors.append("AEH test source count must be one for " + task_id)
    return errors


def compute():
    baseline = _load("protocol/phase2-v1.7/BASELINE.yaml")
    schedule = _load("protocol/phase2-v1.7/SCHEDULE.yaml")
    errors = validate_baseline(baseline) + validate_schedule(schedule)
    return {
        "verdict": "PHASE_2_READINESS_PASS" if not errors else "PHASE_2_READINESS_FAIL",
        "errors": errors,
        "phase2_authorized": baseline.get("phase2_72_run", {}).get("authorized"),
        "planned_blocks": len(schedule.get("blocks") or []),
        "planned_runs": sum(len(block.get("groups") or []) for block in schedule.get("blocks") or []),
    }
