"""Read/write config.json for persistent settings."""

import json
import os
import sys
from pathlib import Path


def _get_config_path() -> Path:
    """Return the path to config.json next to the executable or script."""
    if getattr(sys, "frozen", False):
        base = Path(sys.executable).parent
    else:
        base = Path(__file__).resolve().parent.parent.parent
    return base / "config.json"


def load_config() -> dict:
    """Load configuration from config.json. Returns empty dict if missing."""
    path = _get_config_path()
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_config(config: dict) -> None:
    """Save configuration to config.json."""
    path = _get_config_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def get_templates_folder() -> str:
    """Return the configured templates folder path, or empty string."""
    return load_config().get("templates_folder", "")


def set_templates_folder(folder: str) -> None:
    """Update the templates folder path in config."""
    config = load_config()
    config["templates_folder"] = folder
    save_config(config)
