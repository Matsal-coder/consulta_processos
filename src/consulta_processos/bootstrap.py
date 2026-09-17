from __future__ import annotations

from consulta_processos.database import initialize_database
from consulta_processos.paths import (
    get_config_dir,
    get_data_dir,
    get_env_path,
    get_logs_dir,
    get_monitored_processes_path,
    get_reports_dir,
)

DEFAULT_ENV_CONTENT = """# Configurações do JuriScan

# DataJud / CNJ
DATAJUD_API_KEY=

# Histórico local
ENABLE_LOCAL_HISTORY=true

# Email automático
EMAIL_ENABLED=false
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=
EMAIL_PASSWORD=
EMAIL_FROM=
EMAIL_TO=

# Jobs automáticos
JURISCAN_REPORT_LOOKBACK_DAYS=7
"""


def ensure_env_file() -> None:
    env_path = get_env_path()

    if env_path.exists():
        return

    env_path.write_text(DEFAULT_ENV_CONTENT, encoding="utf-8")


def ensure_monitored_processes_file() -> None:
    monitored_path = get_monitored_processes_path()

    if monitored_path.exists():
        return

    monitored_path.write_text("[]\n", encoding="utf-8")


def bootstrap_local_structure() -> None:
    get_data_dir()
    get_config_dir()
    get_logs_dir()
    get_reports_dir()

    ensure_env_file()
    ensure_monitored_processes_file()
    initialize_database()
