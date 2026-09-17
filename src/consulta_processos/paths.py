from __future__ import annotations

import sys
from pathlib import Path


def is_frozen() -> bool:
    return getattr(sys, "frozen", False)


def get_app_dir() -> Path:
    if is_frozen():
        return Path(sys.executable).resolve().parent

    return Path.cwd().resolve()


def get_data_dir() -> Path:
    path = get_app_dir() / "data"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_config_dir() -> Path:
    path = get_app_dir() / "config"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_logs_dir() -> Path:
    path = get_app_dir() / "logs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_reports_dir() -> Path:
    path = get_app_dir() / "reports"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_env_path() -> Path:
    return get_app_dir() / ".env"


def get_database_path() -> Path:
    return get_data_dir() / "consulta_processos.db"


def get_monitored_processes_path() -> Path:
    return get_config_dir() / "processos_monitorados.json"


def get_log_path() -> Path:
    return get_logs_dir() / "juriscan.log"
