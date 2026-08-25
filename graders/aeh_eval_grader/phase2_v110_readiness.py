"""Deterministic validation for the Phase 2 v1.10 UTF-8 capture candidate."""
import os

from . import phase2_v19_readiness as v19
from .paths import repo_root


PROTOCOL_VERSION = "1.10"
EXPECTED_AEH = v19.EXPECTED_AEH
EXPECTED_ARGV_PREFIX = v19.EXPECTED_ARGV_PREFIX
EXPECTED_CORRECTION = {
    "path": "reports/phase2-preflight-v1.9-verdict.yaml",
    "sha256": "8ceaba8218e2498cf29aca1161807b990b48d7bef0273878f209da99974091b5",
    "verdict": "PREFLIGHT_VALIDATED_WITH_CAPTURE_WARNING",
}
EXPECTED_CAPTURE = {
    "encoding": "utf-8",
    "errors": "replace",
    "applies_to": ["aeh_controller", "codex_session"],
    "no_model_regressions": ["non_ascii_utf8", "invalid_utf8_replacement"],
}
PATH_REPLACEMENTS = {
    "protocol/phase2-v1.9/AMENDMENT-009.md": "protocol/phase2-v1.10/AMENDMENT-010.md",
    "protocol/phase2-v1.9/SCHEDULE.yaml": "protocol/phase2-v1.10/SCHEDULE.yaml",
    "environments/G3-v1.9.yaml": "environments/G3-v1.10.yaml",
    "environments/PHASE_2_RUNBOOK-v1.9.md": "environments/PHASE_2_RUNBOOK-v1.10.md",
}


def expected_input_paths():
    paths = [PATH_REPLACEMENTS.get(path, path) for path in v19.expected_input_paths()]
    paths.extend([
        "graders/tests/test_phase1.py",
        "graders/tests/test_phase2_v110_readiness.py",
    ])
    return sorted(paths)


def render_input_manifest():
    lines = []
    for path in expected_input_paths():
        absolute = os.path.join(repo_root(), *path.split("/"))
        lines.append("%s  %s" % (v19.v18.v17._sha256_file(absolute), path))
    return "\n".join(lines) + "\n"


def validate_schedule(schedule):
    errors = []
    if str(schedule.get("protocol_version")) != PROTOCOL_VERSION:
        errors.append("schedule.protocol_version must be 1.10")
    seed = schedule.get("seed")
    blocks = schedule.get("blocks") or []
    if blocks != v19.v18.v17.expected_blocks(seed or ""):
        errors.append("schedule blocks do not match the deterministic inherited order")
    combinations = {(block.get("task_id"), block.get("repetition")) for block in blocks}
    if len(blocks) != 18 or len(combinations) != 18:
        errors.append("schedule must contain 18 unique task/repetition blocks")
    if sum(len(block.get("groups") or []) for block in blocks) != 72:
        errors.append("schedule must expand to exactly 72 runs")
    return errors


def validate_correction_basis(reference):
    if reference != EXPECTED_CORRECTION:
        return ["v1.9 correction basis reference mismatch"]
    absolute = os.path.join(repo_root(), *reference["path"].split("/"))
    if not os.path.isfile(absolute):
        return ["v1.9 correction basis is missing"]
    errors = []
    if v19.v18.v17._sha256_file(absolute) != reference["sha256"]:
        errors.append("v1.9 correction basis digest mismatch")
    body = v19.v18.v17._load(reference["path"])
    if body.get("verdict") != reference["verdict"]:
        errors.append("v1.9 correction basis verdict mismatch")
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
    if v19.v18.v17._sha256_file(absolute) != expected_hash:
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
    if [path for _, path in entries] != expected_input_paths():
        errors.append("input manifest path set/order does not match the v1.10 contract")
    for expected_digest, input_path in entries:
        full_path = os.path.join(repo_root(), *input_path.split("/"))
        if not os.path.isfile(full_path):
            errors.append("input missing: " + input_path)
        elif v19.v18.v17._sha256_file(full_path) != expected_digest:
            errors.append("input digest mismatch: " + input_path)
    return errors


def validate_baseline(baseline):
    errors = []
    if str(baseline.get("protocol_version")) != PROTOCOL_VERSION:
        errors.append("baseline.protocol_version must be 1.10")
    if baseline.get("status") != "READY_FOR_FORMAL_OWNER_GATE":
        errors.append("baseline status must be READY_FOR_FORMAL_OWNER_GATE")
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
    argv = baseline.get("codex_execution", {}).get("argv_prefix")
    if argv != EXPECTED_ARGV_PREFIX:
        errors.append("Codex argv prefix does not match the validated v1.9 contract")
    if baseline.get("transcript_capture") != EXPECTED_CAPTURE:
        errors.append("transcript capture does not match the v1.10 UTF-8 contract")
    errors.extend(validate_correction_basis(baseline.get("correction_basis") or {}))
    errors.extend(v19.v18.validate_answers(baseline.get("g3_bootstrap_answers") or {}))
    errors.extend(validate_input_manifest(baseline.get("input_manifest") or {}))
    return errors


def compute():
    baseline = v19.v18.v17._load("protocol/phase2-v1.10/BASELINE.yaml")
    schedule = v19.v18.v17._load("protocol/phase2-v1.10/SCHEDULE.yaml")
    errors = validate_baseline(baseline) + validate_schedule(schedule)
    return {
        "verdict": "PHASE_2_V1_10_READINESS_PASS" if not errors else "PHASE_2_V1_10_READINESS_FAIL",
        "errors": errors,
        "phase2_authorized": baseline.get("phase2_72_run", {}).get("authorized"),
        "planned_blocks": len(schedule.get("blocks") or []),
        "planned_runs": sum(len(block.get("groups") or []) for block in schedule.get("blocks") or []),
    }
