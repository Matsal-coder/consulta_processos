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
              AND codigo = ?
              AND descricao = ?
              AND data_movimentacao = ?
            LIMIT 1;
            """,
            (
                numero_processo,
                base,
                atualizacao.codigo,
                atualizacao.descricao,
                atualizacao.data_movimentacao.isoformat(),
            ),
        ).fetchone()

    return row is not None


def salvar_movimento(
    numero_processo: str,
    base: str,
    atualizacao: AtualizacaoProcesso,
    data_ultima_atualizacao_fonte: str | None,
) -> bool:
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
                codigo,
                descricao,
                data_movimentacao,
                orgao_julgador,
                data_ultima_atualizacao_fonte
            )
            VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
            (
                numero_processo,
                base,
                atualizacao.codigo,
                atualizacao.descricao,
                atualizacao.data_movimentacao.isoformat(),
                atualizacao.orgao_julgador,
                data_ultima_atualizacao_fonte,
            ),
        )

    return cursor.rowcount == 1


def salvar_movimentacoes_do_processo(
    numero_processo: str,
    base: str,
    atualizacoes: list[AtualizacaoProcesso],
    data_ultima_atualizacao_fonte: str | None,
) -> int:
    novas = 0

    for atualizacao in atualizacoes:
        foi_nova = salvar_movimento(
            numero_processo=numero_processo,
            base=base,
            atualizacao=atualizacao,
            data_ultima_atualizacao_fonte=data_ultima_atualizacao_fonte,
        )

        if foi_nova:
            novas += 1

    return novas