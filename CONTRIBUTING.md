# Contributing to aeh-evals

This repository is an independent evaluation surface for AEH. Contributions
must preserve evaluator independence, frozen-protocol integrity, and the
public/private evidence boundary.

## Before opening a pull request

1. Keep evaluation tasks, graders, and decisions independent from the AEH
   product repository.
2. Do not rewrite a frozen protocol. Record an explicit amendment or introduce
   a new protocol version when an authorized protocol change is required.
3. Do not commit complete run directories, session logs, transcripts, prompts,
   credentials, or other raw evidence. Public reports may contain redacted
   findings, verdicts, and reproducible hashes only.
4. Preserve the distinction between `task_outcome`, `assurance_outcome`, replay
   execution `status`, and acceptance `overall`.
5. Do not describe Phase 1 or Phase 1.1 as proof of product effectiveness.

## Validation

Run the grader regression suite before submitting:

```text
PYTHONPATH=graders python -m unittest discover -s graders/tests
```

For changes that affect reports or verdicts, also regenerate the applicable
machine report and demonstrate that it matches the committed output.

## Pull request expectations

Describe the evaluation boundary, protocol impact, evidence impact, validation
commands, and any finding or decision IDs affected. Keep unrelated changes in
separate pull requests.
