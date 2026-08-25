"""Deterministic validation for the corrected Phase 2 v1.8 candidate."""
import os

import yaml

from . import phase2_readiness as v17
from .paths import repo_root


PROTOCOL_VERSION = "1.8"
EXPECTED_GROUPS = v17.EXPECTED_GROUPS
EXPECTED_TASKS = v17.EXPECTED_TASKS
EXPECTED_REPETITIONS = v17.EXPECTED_REPETITIONS
EXPECTED_AEH = v17.EXPECTED_AEH
EXPECTED_CODEX_FLAGS = [
    "--model=gpt-5.6-terra",
    "--sandbox=workspace-write",
    "--ask-for-approval=never",
    "--ephemeral",
    "--ignore-user-config",
    "--json",
]
EXPECTED_ANSWERS = {
    "q-git-commit": "deny",
    "q-git-push": "deny",
    "q-human-review": "critical",
    "q-modify-source": "allow",
    "q-plan-before-code": "risk_based",
    "q-shell-access": "allow",
    "q-team-review-policy": "major",
    "q-testing-policy": "risk_based",
    "q-web-access": "deny",
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
    "protocol/phase2-v1.8/AMENDMENT-008.md",
    "protocol/phase2-v1.8/SCHEDULE.yaml",
    "environments/G0.yaml",
    "environments/G1.yaml",
    "environments/G2.yaml",
    "environments/G3-v1.8.yaml",
    "environments/G1-assets/AGENTS.md",
    "environments/G1-assets/context/conventions.md",
    "environments/G3-assets/answers-v1.8.yaml",
    "environments/PHASE_2_RUNBOOK-v1.8.md",
    "graders/cli.py",
]


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
        lines.append("%s  %s" % (v17._sha256_file(absolute), path))
    return "\n".join(lines) + "\n"


def validate_schedule(schedule):
    errors = []
    if str(schedule.get("protocol_version")) != PROTOCOL_VERSION:
        errors.append("schedule.protocol_version must be 1.8")
    seed = schedule.get("seed")
    blocks = schedule.get("blocks") or []
    if blocks != v17.expected_blocks(seed or ""):
        errors.append("schedule blocks do not match the deterministic inherited order")
    combinations = {(block.get("task_id"), block.get("repetition")) for block in blocks}
    if len(blocks) != 18 or len(combinations) != 18:
        errors.append("schedule must contain 18 unique task/repetition blocks")
    if sum(len(block.get("groups") or []) for block in blocks) != 72:
        errors.append("schedule must expand to exactly 72 runs")
    return errors


def validate_answers(reference):
    errors = []
    path = reference.get("path")
    expected_hash = reference.get("sha256")
    if not path or not expected_hash:
        return ["G3 answers reference is incomplete"]
    absolute = os.path.join(repo_root(), *path.split("/"))
    if not os.path.isfile(absolute):
        return ["G3 answers file is missing"]
    if v17._sha256_file(absolute) != expected_hash:
        errors.append("G3 answers digest mismatch")
    body = v17._load(path)
    answers = body.get("answers") or {}
    observed = {question: item.get("answer") for question, item in answers.items()}
    if observed != EXPECTED_ANSWERS:
        errors.append("G3 answers do not match the reviewed headless policy")
    if any(item.get("source") != "user_answer" for item in answers.values()):
        errors.append("G3 answers must carry user_answer provenance")
    return errors


def validate_input_manifest(reference):
    errors = []
    path = reference.get("path")
    expected_hash = reference.get("sha256")
    expected_entries = reference.get("entries")
    if not path or not expected_hash:
        return ["input manifest reference is incomplete"]
    absolute = os.path.join(repo_root(), *path.split("/"))
    if not os.path.isfile(absolute):
        return ["input manifest is missing: " + path]
    if v17._sha256_file(absolute) != expected_hash:
        errors.append("input manifest digest mismatch")
    entries = []
    with open(absolute, "r", encoding="utf-8") as stream:
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
    if paths != expected_input_paths():
        errors.append("input manifest path set/order does not match the v1.8 contract")
    for expected_digest, input_path in entries:
        full_path = os.path.join(repo_root(), *input_path.split("/"))
        if not os.path.isfile(full_path):
            errors.append("input missing: " + input_path)
        elif v17._sha256_file(full_path) != expected_digest:
            errors.append("input digest mismatch: " + input_path)
    return errors


def validate_baseline(baseline):
    errors = []
    if str(baseline.get("protocol_version")) != PROTOCOL_VERSION:
        errors.append("baseline.protocol_version must be 1.8")
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
    flags = baseline.get("codex_execution", {}).get("flags")
    if flags != EXPECTED_CODEX_FLAGS or "--ignore-rules" in (flags or []):
        errors.append("Codex execution flags do not match the corrected v1.8 contract")
    errors.extend(validate_answers(baseline.get("g3_bootstrap_answers") or {}))
    errors.extend(validate_input_manifest(baseline.get("input_manifest") or {}))
    return errors


def compute():
    baseline = v17._load("protocol/phase2-v1.8/BASELINE.yaml")
    schedule = v17._load("protocol/phase2-v1.8/SCHEDULE.yaml")
    errors = validate_baseline(baseline) + validate_schedule(schedule)
    return {
        "verdict": "PHASE_2_V1_8_READINESS_PASS" if not errors else "PHASE_2_V1_8_READINESS_FAIL",
        "errors": errors,
        "phase2_authorized": baseline.get("phase2_72_run", {}).get("authorized"),
        "planned_blocks": len(schedule.get("blocks") or []),
        "planned_runs": sum(len(block.get("groups") or []) for block in schedule.get("blocks") or []),
    }
