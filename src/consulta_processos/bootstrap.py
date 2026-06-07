from __future__ import annotations

from consulta_processos.paths import (
    get_config_dir,
    get_data_dir,
    get_env_path,
    get_logs_dir,
    get_monitored_processes_path,
    get_reports_dir,
)

DEFAULT_ENV_CONTENT = """ENABLE_LOCAL_HISTORY=true
DATAJUD_API_KEY=
"""


def ensure_env_file() -> None:
    env_path = get_env_path()

    if not env_path.exists():
        env_path.write_text(
            DEFAULT_ENV_CONTENT,
            encoding="utf-8",
        )


def ensure_monitored_processes_file() -> None:
    monitorados_path = get_monitored_processes_path()

    if not monitorados_path.exists():
        monitorados_path.write_text(
            "[]",
            encoding="utf-8",
        )


def bootstrap_local_structure() -> None:
    get_data_dir()
    get_config_dir()
    get_logs_dir()
    get_reports_dir()

    ensure_env_file()
    ensure_monitored_processes_file()