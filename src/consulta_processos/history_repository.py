from consulta_processos.database import get_connection
from consulta_processos.models import AtualizacaoProcesso


def movimento_existe(
    numero_processo: str,
    base: str,
    atualizacao: AtualizacaoProcesso,
) -> bool:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT 1
            FROM movimentacoes_consultadas
            WHERE numero_processo = ?
              AND base = ?
              AND descricao = ?
              AND data_movimentacao = ?
            LIMIT 1;
            """,
            (
                numero_processo,
                base,
                atualizacao.descricao,
                atualizacao.data_movimentacao.isoformat(),
            ),
        ).fetchone()

    return row is not None


def salvar_movimento(numero_processo: str, base: str, atualizacao: AtualizacaoProcesso) -> bool:
    """
    Salva uma movimentação no histórico local.

    Retorna True se a movimentação for nova.
    Retorna False se ela já existia.
    """
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT OR IGNORE INTO movimentacoes_consultadas (
                numero_processo,
                base,
                descricao,
                data_movimentacao
            )
            VALUES (?, ?, ?, ?);
            """,
            (
                numero_processo,
                base,
                atualizacao.descricao,
                atualizacao.data_movimentacao.isoformat(),
            ),
        )

    return cursor.rowcount == 1


def salvar_movimentacoes_do_processo(
    numero_processo: str,
    base: str,
    atualizacoes: list[AtualizacaoProcesso],
) -> int:
    novas = 0

    for atualizacao in atualizacoes:
        foi_nova = salvar_movimento(
            numero_processo=numero_processo,
            base=base,
            atualizacao=atualizacao,
        )

        if foi_nova:
            novas += 1

    return novas


def marcar_movimentacoes_novas(
    numero_processo: str,
    base: str,
    atualizacoes: list[AtualizacaoProcesso],
) -> list[AtualizacaoProcesso]:
    atualizacoes_marcadas = []

    for atualizacao in atualizacoes:
        existe = movimento_existe(
            numero_processo=numero_processo,
            base=base,
            atualizacao=atualizacao,
        )

        atualizacoes_marcadas.append(
            atualizacao.model_copy(
                update={"nova": not existe},
            )
        )

    return atualizacoes_marcadas


def listar_movimentacoes_salvas() -> list[dict]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                numero_processo,
                base,
                descricao,
                data_movimentacao,
                created_at
            FROM movimentacoes_consultadas
            ORDER BY data_movimentacao DESC;
            """
        ).fetchall()

    return [dict(row) for row in rows]
