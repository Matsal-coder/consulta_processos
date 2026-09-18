import sqlite3
from pathlib import Path

from consulta_processos.paths import get_database_path as default_database_path
from consulta_processos.settings import get_settings

DEFAULT_DB_NAME = "consulta_processos.db"


def get_database_path() -> Path:
    settings = get_settings()

    if settings.consulta_processos_db_path:
        return settings.consulta_processos_db_path

    return default_database_path()


def get_connection() -> sqlite3.Connection:
    db_path = get_database_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS movimentacoes_consultadas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_processo TEXT NOT NULL,
                base TEXT NOT NULL,
                descricao TEXT NOT NULL,
                data_movimentacao TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                comentario TEXT,
                UNIQUE (
                    numero_processo,
                    base,
                    descricao,
                    data_movimentacao
                )
            );
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS processos_cadastrados (
                numero_processo TEXT NOT NULL,
                base TEXT NOT NULL,
                cliente TEXT NOT NULL,
                apelido TEXT,
                monitorado INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                PRIMARY KEY (
                    numero_processo,
                    base
                )
            );
            """
        )
