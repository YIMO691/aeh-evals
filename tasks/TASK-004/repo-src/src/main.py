"""Entrypoint wiring config and service."""

from config import load_config
from service import top_items


def run(records, config_path=None):
    load_config(config_path)
    return top_items(records)
