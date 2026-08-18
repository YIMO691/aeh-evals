"""Config file loader (key=value)."""


def load_config(path=None):
    cfg = {"limit": 10}
    if path:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                cfg[key.strip()] = int(value.strip()) if key.strip() == "limit" else value.strip()
    return cfg
