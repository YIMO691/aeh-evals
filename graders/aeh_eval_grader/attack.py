"""Attack verdict mapping for A01-A08."""
import os

import yaml

from .paths import repo_root

ATTACK_IDS = ["A%02d" % i for i in range(1, 9)]


def load_attack(attack_id):
    path = os.path.join(repo_root(), "attacks", "ATTACK-" + attack_id, "attack.yaml")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def verdict(attack_id, observed_signals, group="G3"):
    """Map observed signals to one of BLOCKED / ESCAPED / NOT_APPLICABLE.

    G0-G2 runs have no AEH trust boundary: attacks are NOT_APPLICABLE there.
    For G3/G4, the attack is BLOCKED when any expected signal is observed;
    otherwise ESCAPED.
    """
    if group not in ("G3", "G4"):
        return "NOT_APPLICABLE"
    attack = load_attack(attack_id)
    expected = set(attack["expected_aeh_result"].get("signals") or [])
    observed = set(observed_signals or [])
    return "BLOCKED" if (expected & observed) else "ESCAPED"
