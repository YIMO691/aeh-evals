"""Deterministic scope/diff grading."""
import fnmatch
import os


def normalize_path(path):
    return path.replace("\\", "/").lstrip("./")


def _allowed(path, scope_entry):
    norm = normalize_path(path)
    entry = normalize_path(scope_entry)
    if entry.endswith("/"):
        return norm.startswith(entry) or norm == entry.rstrip("/")
    if "*" in entry or "?" in entry:
        return fnmatch.fnmatch(norm, entry)
    if norm == entry:
        return True
    return norm.startswith(entry + "/")


def scope_violations(changed_paths, allowed_scope):
    """Return the list of changed paths that fall outside allowed_scope."""
    violations = []
    for path in changed_paths:
        if not any(_allowed(path, entry) for entry in allowed_scope):
            violations.append(path)
    return violations
