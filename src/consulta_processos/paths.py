from __future__ import annotations

import sys
from pathlib import Path


def get_app_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent

    return Path.cwd()


def get_data_dir() -> Path:
    path = get_app_dir() / "data"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_config_dir() -> Path:
    path = get_app_dir() / "config"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_env_path() -> Path:
    return get_app_dir() / ".env"