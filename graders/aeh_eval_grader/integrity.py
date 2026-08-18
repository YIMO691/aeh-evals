"""Static integrity checks for machine-truth artifacts.

This grader intentionally does NOT import the AEH package: it re-checks the
artifacts from the frozen V0.1 semantics documented in the AEH repository, so
the evaluated project cannot grade its own exam.
"""
import hashlib
import os


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def red_forgery(artifact):
    """Reject RED artifacts that claim PASS without real machine outputs.

    Returns (ok, reason). A real RED artifact records command outputs; a forged
    one typically claims overall=PASS with empty outputs.
    """
    overall = artifact.get("overall") or artifact.get("status")
    outputs = artifact.get("outputs") or artifact.get("test_outputs") or []
    if str(overall).upper() in ("PASS", "VALID_RED") and not outputs:
        return False, "claims PASS/VALID_RED but has no machine outputs"
    return True, ""


def verification_forgery(artifact):
    """Reject verification artifacts claiming success without referenced evidence."""
    overall = artifact.get("overall")
    if str(overall).upper() in ("PASS", "MERGE_READY"):
        refs = artifact.get("evidence") or artifact.get("evidence_refs") or []
        if not refs:
            return False, "claims success but references no evidence"
    return True, ""


def check_runtime_digest(manifest_path, runtime_dir):
    """Compare manifest source_hashes.runtime against the current runtime tree.

    Uses the same core/schemas file hashing approach as AEH V0.1 doctor so a
    tampered contract is detected independently.
    """
    import yaml

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = yaml.safe_load(f)
    expected = (manifest.get("source_hashes") or {}).get("runtime")
    parts = []
    for folder in ("core", "schemas"):
        d = os.path.join(runtime_dir, folder)
        if not os.path.isdir(d):
            return False, "runtime folder missing: " + folder
        for fname in sorted(os.listdir(d)):
            p = os.path.join(d, fname)
            if not os.path.isfile(p):
                continue
            parts.append(folder + "/" + fname + "\0" + sha256_file(p))
    actual = hashlib.sha256(("\n".join(sorted(parts))).encode("utf-8")).hexdigest()
    if actual != expected:
        return False, "runtime digest mismatch: manifest=%s actual=%s" % (expected, actual)
    return True, ""
