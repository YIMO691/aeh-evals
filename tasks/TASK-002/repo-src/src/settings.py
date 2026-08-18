"""Settings loader with an in-process cache."""

_CACHE = {}


def load_settings(path):
    """Load key=value settings from a text file."""
    if path in _CACHE:
        return _CACHE[path]
    data = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            data[key.strip()] = value.strip()
    _CACHE[path] = data
    return data


def get(path, key, default=None):
    return load_settings(path).get(key, default)
