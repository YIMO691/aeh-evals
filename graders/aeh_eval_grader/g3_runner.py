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


def _log(evidence_dir, name, text):
    with open(os.path.join(evidence_dir, name), "w", encoding="utf-8") as f:
        f.write(text)
    return text


def _run_aeh(aeh, args, workdir, evidence_dir, step_name):
    cmd = [aeh] + args + ["--workdir", workdir]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
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
    code, status, out = _run_aeh(args.aeh, ["bootstrap", workdir], workdir,
                                 args.evidence_dir, "01-bootstrap")
    steps.append(("bootstrap", code, status))
    if code != 0 or status != "BOOTSTRAP_COMPLETE":
        return stop("bootstrap code=%s status=%s" % (code, status))

    # 2. doctor (pre)
    code, status, out = _run_aeh(args.aeh, ["doctor", workdir], workdir,
                                 args.evidence_dir, "02-doctor-pre")
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

    # 8. Codex coding task only
    with open(args.prompt_file, "r", encoding="utf-8") as f:
        prompt = f.read().strip()
    last_msg = os.path.join(args.evidence_dir, "agent-last-message.txt")
    codex_cmd = [args.codex, "exec", "-C", workdir] + list(args.codex_extra) \
        + ["-o", last_msg, prompt]
    started = time.time()
    proc = subprocess.run(codex_cmd, capture_output=True, text=True, timeout=1800)
    elapsed = int(time.time() - started)
    session = (proc.stdout or "") + (proc.stderr or "")
    _log(args.evidence_dir, "session.log", session)
    _log(args.evidence_dir, "run-meta.txt",
         "started_at=%d\nfinished_at=%d\ncodex_exit=%d\n" % (started, started + elapsed, proc.returncode))
    steps.append(("codex", proc.returncode, "exit=%d" % proc.returncode))
    if proc.returncode != 0:
        return stop("codex exit=%d" % proc.returncode)

    # 9. green with dynamically computed scope hashes
    after = _sha256_file(os.path.join(workdir, "src", "main.py"))
    proc = subprocess.run(["git", "-C", workdir, "show", "HEAD:src/main.py"],
                          capture_output=True, text=True)
    before = hashlib.sha256(proc.stdout.encode("utf-8")).hexdigest() if proc.returncode == 0 else ""
    with open(args.scope_template, "r", encoding="utf-8") as f:
        scope_text = f.read().replace("TO_BE_FILLED_AFTER_HASH", after)
    scope_path = os.path.join(args.evidence_dir, "scope-applied.yaml")
    with open(scope_path, "w", encoding="utf-8") as f:
        f.write(scope_text)
    _log(args.evidence_dir, "scope-hashes.txt", "before=%s\nafter=%s\n" % (before, after))
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
