# top-service conventions (project skill stand-in, frozen)

- Config loader semantics: `load_config()` returns `{"limit": <int>}` with default 10;
  config files are key=value with `#` comments.
- `top_items` preserves input order and returns at most `limit` records.
- `run()` is the public entrypoint used by the application shell.
- No third-party dependencies are allowed.
- Test command (from repo root): `PYTHONPATH=src python -m unittest discover -s tests -t .`
