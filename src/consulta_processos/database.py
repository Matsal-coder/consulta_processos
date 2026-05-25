import os
import sqlite3
from pathlib import Path

from consulta_processos.paths import get_data_dir

DEFAULT_DB_NAME = "consulta_processos.db"


def get_database_path() -> Path:
    custom_path = os.getenv("CONSULTA_PROCESSOS_DB_PATH")

    if custom_path:
        return Path(custom_path)

    return get_data_dir() / DEFAULT_DB_NAME


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
                codigo INTEGER NOT NULL,
                descricao TEXT NOT NULL,
                data_movimentacao TEXT NOT NULL,
                orgao_julgador TEXT,
                data_ultima_atualizacao_fonte TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (
                    numero_processo,
                    base,
                    codigo,
                    descricao,
                    data_movimentacao
                )
            );
            """
        )