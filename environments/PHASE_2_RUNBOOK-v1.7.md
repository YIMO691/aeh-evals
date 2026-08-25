# PHASE 2 v1.7 — 72-Run Candidate Runbook

> Status: `STOP / READY_FOR_PREFLIGHT`. This document does not authorize a benchmark run.

## 1. Authority and baseline gates

Before any run:

1. `python -m graders.cli phase2-readiness` must print `PHASE_2_READINESS_PASS`.
2. Owner must approve the exact Agent/model/environment fields and separately authorize preflight
   or formal execution.
3. G3 must install the exact wheel in `protocol/phase2-v1.7/BASELINE.yaml` and verify its SHA-256
   before installation. A source checkout, editable install, newer commit, or same-version foreign
   wheel is not an equivalent treatment.
4. Freeze Agent version/model, OS, Python, sandbox, network and timeout into every run manifest.

## 2. One canonical execution order

Use `protocol/phase2-v1.7/SCHEDULE.yaml` exactly as committed. Each block is one task/repetition and
contains G0–G3 once in its frozen order. Every entry uses a fresh work directory and a fresh Agent
session. No transcript, context, `.aeh` directory or process state may cross run boundaries.

This rule replaces the conflicting group-first paragraph in the historical v1.6 RUNBOOK for v1.7
only. The v1.6 file remains immutable evidence.

## 3. Per-run procedure

1. Restore `tasks/<TASK>/repo-src.bundle` at the task's frozen commit and verify a clean tree.
2. Apply the selected G0–G3 environment. G1 assets are identical in G1–G3; G2 adds the frozen Spec
   layer; G3 adds only External AEH Assurance.
3. For G3, invoke the generic runner with that task's `aeh-inputs/{reqs,plan}.yaml`,
   `aeh-inputs/scope-v1.7.yaml` and `aeh-inputs/test-src/`. The Controller captures source
   before-hashes after VALID_RED and before invoking the Agent; this avoids CRLF/LF drift without
   trusting an Agent-supplied baseline.
4. Preserve raw local evidence, run deterministic graders outside the Agent session, and fill
   `task_outcome`, `assurance_outcome`, both false-completion fields and integrity observations.
5. Validate cross-group freeze fields and hidden-test secrecy before accepting the run.

## 4. Lock and abort policy

After formal execution starts, protocol, tasks, graders, schedule and AEH artifact are immutable.
An AEH failure is recorded without a product fix. A protocol or grader defect aborts the entire
formal experiment; issue a new protocol version and restart all formal runs.

Benchmark results and A01–A08 adversarial results remain separate reports. Conclusions are limited
to the frozen Python pilot task distribution.
