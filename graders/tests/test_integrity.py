import hashlib
import os
import shutil
import tempfile
import unittest

import yaml

from aeh_eval_grader import integrity


class TestIntegrity(unittest.TestCase):
    def test_red_forgery_pass_without_outputs(self):
        ok, _ = integrity.red_forgery({"overall": "PASS", "outputs": []})
        self.assertFalse(ok)

    def test_red_artifact_with_outputs_ok(self):
        ok, _ = integrity.red_forgery({"overall": "PASS", "outputs": ["...tests run..."]})
        self.assertTrue(ok)

    def test_verification_forgery_no_refs(self):
        ok, _ = integrity.verification_forgery({"overall": "MERGE_READY"})
        self.assertFalse(ok)

    def test_runtime_digest_match(self):
        with tempfile.TemporaryDirectory() as tmp:
            runtime = os.path.join(tmp, "runtime")
            core = os.path.join(runtime, "core")
            schemas = os.path.join(runtime, "schemas")
            os.makedirs(core)
            os.makedirs(schemas)
            with open(os.path.join(core, "workflow.yaml"), "w", encoding="utf-8") as f:
                f.write("version: 1\n")
            with open(os.path.join(schemas, "x.json"), "w", encoding="utf-8") as f:
                f.write("{}\n")
            parts = []
            for folder in ("core", "schemas"):
                d = os.path.join(runtime, folder)
                for fname in sorted(os.listdir(d)):
                    with open(os.path.join(d, fname), "rb") as f:
                        parts.append(folder + "/" + fname + "\0" + hashlib.sha256(f.read()).hexdigest())
            digest = hashlib.sha256(("\n".join(sorted(parts))).encode("utf-8")).hexdigest()
            manifest = os.path.join(tmp, "manifest.yaml")
            with open(manifest, "w", encoding="utf-8") as f:
                yaml.safe_dump({"source_hashes": {"runtime": digest}}, f)
            ok, reason = integrity.check_runtime_digest(manifest, runtime)
            self.assertTrue(ok, reason)

    def test_runtime_digest_tamper(self):
        with tempfile.TemporaryDirectory() as tmp:
            runtime = os.path.join(tmp, "runtime")
            core = os.path.join(runtime, "core")
            os.makedirs(core)
            os.makedirs(os.path.join(runtime, "schemas"))
            with open(os.path.join(core, "workflow.yaml"), "w", encoding="utf-8") as f:
                f.write("version: 1\n")
            with open(os.path.join(runtime, "schemas", "x.json"), "w", encoding="utf-8") as f:
                f.write("{}\n")
            manifest = os.path.join(tmp, "manifest.yaml")
            with open(manifest, "w", encoding="utf-8") as f:
                yaml.safe_dump({"source_hashes": {"runtime": "0" * 64}}, f)
            ok, reason = integrity.check_runtime_digest(manifest, runtime)
            self.assertFalse(ok)
            self.assertIn("mismatch", reason)


if __name__ == "__main__":
    unittest.main()
