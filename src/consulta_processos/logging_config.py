import logging
from pathlib import Path

from consulta_processos.paths import get_app_dir


LOG_FORMAT = (
    "%(asctime)s | %(levelname)s | "
    "%(name)s | %(message)s"
)


def get_log_path() -> Path:
    log_dir = get_app_dir() / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    return log_dir / "juriscan.log"


def configure_logging() -> None:
    log_path = get_log_path()

    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        handlers=[
            logging.FileHandler(
                log_path,
                encoding="utf-8",
            ),
            logging.StreamHandler(),
        ],
        force=True,
    )