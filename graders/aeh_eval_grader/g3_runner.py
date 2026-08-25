"""G3 External AEH Assurance Runner (route B, protocol v1.6).

Eval Controller drives the AEH CLI end-to-end; Codex is invoked only for the
coding task between RED and GREEN and never owns any gate.

Usage:
  python -m graders.aeh_eval_grader.g3_runner \
    --workdir <dir> --aeh <aeh.exe> --codex <codex.exe> \
    --title "..." --reqs <reqs.yaml> --plan <plan.yaml> \
    --scope-template <scope.yaml> --test-src <dir> \
    --prompt-file <prompt.txt> --evidence-dir <dir> \
    [--codex-extra --dangerously-bypass-approvals-and-sandbox]
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time

import yaml


def _log(evidence_dir, name, text):
    with open(os.path.join(evidence_dir, name), "w", encoding="utf-8") as f:
        f.write(text)
    return text


def _build_aeh_command(aeh, args, workdir, add_workdir_option=True):
    """Build an AEH command without changing positional target semantics.

    ``bootstrap`` and ``doctor`` receive their target as a positional argument.
    Change subcommands receive the target through ``--workdir``.
    """
    cmd = [aeh] + list(args)
    if add_workdir_option:
        cmd += ["--workdir", workdir]
    return cmd


def _bootstrap_arguments(workdir, answers=None):
    """Build bootstrap arguments, preserving the v1.7 no-answers compatibility path."""
    arguments = ["bootstrap", workdir]
    if answers:
        arguments += ["--answers", os.path.abspath(answers)]
    return arguments


def _run_captured(command, timeout):
    """Capture UTF-8 CLI output without depending on the Windows ANSI code page."""
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )


def _run_aeh(aeh, args, workdir, evidence_dir, step_name, add_workdir_option=True):
    cmd = _build_aeh_command(aeh, args, workdir, add_workdir_option)
    proc = _run_captured(cmd, timeout=300)
    out = (proc.stdout or "") + (proc.stderr or "")
    _log(evidence_dir, "aeh-controller-%s.txt" % step_name, out)
    status = None
    try:
        data = json.loads(proc.stdout or "{}")
        if isinstance(data, dict):
            status = data.get("status") or data.get("overall")
    except Exception:
        for marker in ("BLOCKED", "COMPLETE", "READY", "INVALID"):
            if marker in out:
                status = marker
                break
    return proc.returncode, status, out


def _change_id(workdir):
    changes = os.path.join(workdir, ".aeh", "changes")
    ids = sorted(d for d in os.listdir(changes) if d.startswith("CHG-"))
    return ids[0] if ids else None


def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_scope_template(scope_template):
    with open(scope_template, "r", encoding="utf-8") as stream:
        return yaml.safe_load(stream)


def _capture_scope_before(scope_template, workdir, evidence_dir):
    """Capture working-tree bytes after RED and before the coding Agent runs."""
    scope = _load_scope_template(scope_template)
    changed_files = scope.get("changed_files") or []
    if not changed_files:
        raise ValueError("scope template has no changed_files")
    root = os.path.realpath(workdir)
    snapshot = {}
    for item in changed_files:
        relative_path = str(item.get("path") or "").replace("\\", "/")
        if not relative_path:
            raise ValueError("scope changed_files entry has no path")
        absolute_path = os.path.realpath(os.path.join(root, *relative_path.split("/")))
        if os.path.commonpath([root, absolute_path]) != root:
            raise ValueError("scope path escapes workdir: " + relative_path)
        if not os.path.isfile(absolute_path):
            raise ValueError("scope path does not exist before coding: " + relative_path)
        clean = subprocess.run(
            ["git", "-C", workdir, "diff", "--quiet", "--", relative_path])
        if clean.returncode != 0:
            raise ValueError("scope path is dirty before coding: " + relative_path)
        before_hash = _sha256_file(absolute_path)
        expected_before = item.get("before_hash")
        if expected_before not in (None, "TO_BE_CAPTURED_BEFORE_CODE", before_hash):
            raise ValueError("scope before_hash mismatch: " + relative_path)
        snapshot[relative_path] = before_hash

    snapshot_path = os.path.join(evidence_dir, "scope-before.yaml")
    with open(snapshot_path, "w", encoding="utf-8") as stream:
        yaml.safe_dump({"before_hashes": snapshot}, stream, sort_keys=True)
    return snapshot


def _materialize_scope(scope_template, workdir, evidence_dir, before_snapshot):
    """Fill task-specific scope hashes without assuming a source-file name."""
    scope = _load_scope_template(scope_template)
    changed_files = scope.get("changed_files") or []
    root = os.path.realpath(workdir)
    hash_lines = []
    for item in changed_files:
        relative_path = str(item.get("path") or "").replace("\\", "/")
        absolute_path = os.path.realpath(os.path.join(root, *relative_path.split("/")))
        if os.path.commonpath([root, absolute_path]) != root:
            raise ValueError("scope path escapes workdir: " + relative_path)
        if not os.path.isfile(absolute_path):
            raise ValueError("scope path does not exist after coding: " + relative_path)
        before_hash = before_snapshot.get(relative_path)
        if not before_hash:
            raise ValueError("scope path has no trusted before snapshot: " + relative_path)
        after_hash = _sha256_file(absolute_path)
        item["before_hash"] = before_hash
        item["after_hash"] = after_hash
        hash_lines.append("%s before=%s after=%s" % (relative_path, before_hash, after_hash))

    scope_path = os.path.join(evidence_dir, "scope-applied.yaml")
    with open(scope_path, "w", encoding="utf-8") as stream:
        yaml.safe_dump(scope, stream, sort_keys=False, allow_unicode=True)
    _log(evidence_dir, "scope-hashes.txt", "\n".join(hash_lines) + "\n")
    return scope_path


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--workdir", required=True)
    parser.add_argument("--aeh", required=True)
    parser.add_argument("--codex", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--reqs", required=True)
    parser.add_argument("--plan", required=True)
    parser.add_argument("--scope-template", required=True)
    parser.add_argument("--test-src", required=True)
    parser.add_argument("--prompt-file", required=True)
    parser.add_argument("--evidence-dir", required=True)
    parser.add_argument("--answers", default=None)
    parser.add_argument("--codex-extra", nargs="*", default=[])
    args = parser.parse_args(argv)

    os.makedirs(args.evidence_dir, exist_ok=True)
    workdir = os.path.abspath(args.workdir)
    steps = []

    def stop(reason):
        _log(args.evidence_dir, "RUNNER_STOP.txt", reason)
        print("RUNNER_STOP " + reason)
        return 2

    # 1. bootstrap
    code, status, out = _run_aeh(args.aeh, _bootstrap_arguments(workdir, args.answers), workdir,
                                 args.evidence_dir, "01-bootstrap",
                                 add_workdir_option=False)
    steps.append(("bootstrap", code, status))
    if code != 0 or status != "BOOTSTRAP_COMPLETE":
        return stop("bootstrap code=%s status=%s" % (code, status))

    # 2. doctor (pre)
    code, status, out = _run_aeh(args.aeh, ["doctor", workdir], workdir,
                                 args.evidence_dir, "02-doctor-pre",
                                 add_workdir_option=False)
    steps.append(("doctor_pre", code, status))
    if status not in ("READY", "READY_WITH_WARNINGS"):
        return stop("doctor_pre status=%s" % status)

    # 3. change new
    code, status, out = _run_aeh(args.aeh, ["change", "new", args.title], workdir,
                                 args.evidence_dir, "03-change-new")
    steps.append(("change_new", code, status))
    if code != 0 or status != "CHANGE_CREATED":
        return stop("change_new code=%s status=%s" % (code, status))
    change_id = _change_id(workdir)
    if not change_id:
        return stop("change id not found")

    # 4. ground
    code, status, out = _run_aeh(args.aeh, ["change", "ground", change_id], workdir,
                                 args.evidence_dir, "04-ground")
    steps.append(("ground", code, status))
    if code != 0 or status != "GROUNDING_COMPLETE":
        return stop("ground status=%s" % status)

    # 5. spec
    code, status, out = _run_aeh(args.aeh, ["change", "spec", change_id, "--reqs", args.reqs],
                                 workdir, args.evidence_dir, "05-spec")
    steps.append(("spec", code, status))
    if code != 0 or status != "SPEC_COMPLETE":
        return stop("spec status=%s" % status)

    # 6. test-design
    code, status, out = _run_aeh(args.aeh,
                                 ["change", "test-design", change_id,
                                  "--plan", args.plan, "--test-src", args.test_src],
                                 workdir, args.evidence_dir, "06-test-design")
    steps.append(("test_design", code, status))
    if code != 0 or status != "TEST_DESIGN_COMPLETE":
        return stop("test_design status=%s" % status)

    # 7. red
    code, status, out = _run_aeh(args.aeh, ["change", "red", change_id], workdir,
                                 args.evidence_dir, "07-red")
    steps.append(("red", code, status))
    if status != "RED_COMPLETE" or "VALID_RED" not in out:
        return stop("red status=%s (expected RED_COMPLETE + VALID_RED)" % status)

    try:
        scope_before = _capture_scope_before(
            args.scope_template, workdir, args.evidence_dir)
    except ValueError as error:
        return stop("scope before capture: " + str(error))

    # 8. Codex coding task only
    with open(args.prompt_file, "r", encoding="utf-8") as f:
        prompt = f.read().strip()
    last_msg = os.path.join(args.evidence_dir, "agent-last-message.txt")
    codex_cmd = [args.codex, "exec", "-C", workdir] + list(args.codex_extra) \
        + ["-o", last_msg, prompt]
    started = time.time()
    proc = _run_captured(codex_cmd, timeout=1800)
    elapsed = int(time.time() - started)
    session = (proc.stdout or "") + (proc.stderr or "")
    _log(args.evidence_dir, "session.log", session)
    _log(args.evidence_dir, "run-meta.txt",
         "started_at=%d\nfinished_at=%d\ncodex_exit=%d\n" % (started, started + elapsed, proc.returncode))
    steps.append(("codex", proc.returncode, "exit=%d" % proc.returncode))
    if proc.returncode != 0:
        return stop("codex exit=%d" % proc.returncode)

    # 9. green with dynamically computed task-specific scope hashes
    try:
        scope_path = _materialize_scope(
            args.scope_template, workdir, args.evidence_dir, scope_before)
    except ValueError as error:
        return stop("scope materialization: " + str(error))
    code, status, out = _run_aeh(args.aeh, ["change", "green", change_id, "--scope", scope_path],
                                 workdir, args.evidence_dir, "08-green")
    steps.append(("green", code, status))
    if status != "GREEN_COMPLETE":
        return stop("green status=%s" % status)

    # 10. verify (also serves as validator replay evidence)
    code, status, out = _run_aeh(args.aeh, ["change", "verify", change_id], workdir,
                                 args.evidence_dir, "09-verify")
    steps.append(("verify", code, status))
    _log(args.evidence_dir, "aeh-replay-verify.txt", out)
    if status not in ("VERIFY_COMPLETE", "MERGE_READY", "READY_WITH_WARNINGS", "BLOCKED"):
        return stop("verify status=%s" % status)

    summary = json.dumps({"change_id": change_id, "steps": steps,
                          "final_status": status}, ensure_ascii=False, indent=2)
    _log(args.evidence_dir, "controller-summary.txt", summary)
    print("RUNNER_OK change_id=%s final_status=%s" % (change_id, status))
    return 0


if __name__ == "__main__":
    sys.exit(main())
