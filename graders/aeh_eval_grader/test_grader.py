"""Test execution and failure-signature classification (USER_RUNTIME wrapper).

The functions here are deterministic; the test run itself is performed by the
human operator in the frozen environment. Graders only classify recorded output.
"""
import os
import subprocess

ENV_FAILURE_MARKERS = [
    "ModuleNotFoundError",
    "ImportError",
    "No module named",
    "FileNotFoundError",
    "PermissionError",
]


def classify_failure(output):
    """Classify a failing test run.

    Returns one of:
      PASS                 - zero exit
      ENVIRONMENT_FAILURE  - import/env markers present
      TEST_FAILURE         - tests failed for assertion reasons
    """
    text = output or ""
    if not text:
        return "NO_OUTPUT"
    if any(m in text for m in ENV_FAILURE_MARKERS):
        return "ENVIRONMENT_FAILURE"
    return "TEST_FAILURE"


def valid_red(output):
    """A RED is valid only when tests failed for assertion reasons."""
    return classify_failure(output) == "TEST_FAILURE"


def run_tests(repo, start_dir, top_dir=None, pythonpath=None, timeout=120):
    """Run unittest discovery and capture the result (uses real subprocess)."""
    env = dict(os.environ)
    if pythonpath:
        env["PYTHONPATH"] = pythonpath + os.pathsep + env.get("PYTHONPATH", "")
    cmd = [env.get("PYTHON", os.sys.executable) or os.sys.executable,
           "-m", "unittest", "discover", "-s", start_dir]
    if top_dir:
        cmd += ["-t", top_dir]
    proc = subprocess.run(cmd, cwd=repo, env=env, capture_output=True,
                          text=True, timeout=timeout)
    output = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode, output
