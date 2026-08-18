# top-service — Project Context (G1/G2/G3 frozen asset)

This is a small Python service that trims record lists. Repository layout:

- `src/config.py` — key=value config loader (default limit = 10)
- `src/service.py` — `top_items(records, limit)` trimming service
- `src/main.py` — `run(records, config_path=None)` entrypoint wiring
- `tests/` — existing regression tests

Project conventions:

1. Keep every existing test green; do not edit files under `tests/`.
2. Change only what the task asks for; do not restructure unrelated modules.
3. Run tests with `PYTHONPATH=src python -m unittest discover -s tests -t .`.
4. Prefer the smallest correct change over rewrites.
