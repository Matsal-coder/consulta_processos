from __future__ import annotations

from consulta_processos.database import (
    get_connection,
)


def salvar_processo(
    numero_processo: str,
    base: str,
    cliente: str,
    apelido: str | None = None,
) -> bool:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT OR IGNORE INTO processos_cadastrados (
                numero_processo,
                base,
                cliente,
                apelido
            )
            VALUES (?, ?, ?, ?);
            """,
            (
                numero_processo,
                base,
                cliente,
                apelido,
            ),
        )

    return cursor.rowcount == 1


def listar_clientes() -> list[str]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT DISTINCT cliente
            FROM processos_cadastrados
            ORDER BY cliente;
            """
        ).fetchall()

    return [
        row["cliente"]
        for row in rows
    ]


def listar_processos_por_cliente(
    cliente: str,
) -> list[dict]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                numero_processo,
                base,
                cliente,
                apelido,
                created_at
            FROM processos_cadastrados
            WHERE cliente = ?
            ORDER BY created_at DESC;
            """,
            (cliente,),
        ).fetchall()

    return [dict(row) for row in rows]


def atualizar_apelido(
    numero_processo: str,
    base: str,
    apelido: str,
) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE processos_cadastrados
            SET apelido = ?
            WHERE numero_processo = ?
              AND base = ?;
            """,
            (
                apelido,
                numero_processo,
                base,
            ),
        )


def salvar_comentario_movimentacao(
    movimentacao_id: int,
    comentario: str,
) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE movimentacoes_consultadas
            SET comentario = ?
            WHERE id = ?;
            """,
            (
                comentario,
                movimentacao_id,
            ),
        )

def listar_movimentacoes_processo(
    numero_processo: str,
    base: str,
) -> list[dict]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                numero_processo,
                base,
                descricao,
                data_movimentacao,
                comentario,
                created_at
            FROM movimentacoes_consultadas
            WHERE numero_processo = ?
              AND base = ?
            ORDER BY data_movimentacao DESC;
            """,
            (
                numero_processo,
                base,
            ),
        ).fetchall()

    return [dict(row) for row in rows]

def remover_processo(
    numero_processo: str,
    base: str,
) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            DELETE FROM processos_cadastrados
            WHERE numero_processo = ?
              AND base = ?;
            """,
            (
                numero_processo,
                base,
            ),
        )