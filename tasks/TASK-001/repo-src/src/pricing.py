"""Pricing helpers for the demo store."""


def clamp_percent(pct):
    """Clamp a percentage to [0, 100]."""
    if pct > 100:
        return 100
    if pct < 0:
        return 0
    return pct


def apply_discount(total, percent):
    """Return the discounted total for a percentage discount."""
    p = clamp_percent(percent)
    return round(total * (1 - p / 100), 2)


def format_price(cents):
    """Format an integer amount of cents as a two-decimal price string."""
    if cents % 100 == 0:
        return str(cents // 100)
    return f"{cents / 100:.2f}"
