from datetime import date, datetime

from consulta_processos.datajud_client import DataJudClient
from consulta_processos.models import (
    AtualizacaoProcesso,
    ResultadoConsultaProcesso,
)


def consultar_processo_datajud_tjrj(
    numero_processo: str,
    data_base: date,
    api_key: str,
) -> ResultadoConsultaProcesso:
    client = DataJudClient(api_key=api_key)

    data = client.buscar_processo(
        tribunal="tjrj",
        numero_processo=numero_processo,
    )

    hits = data["hits"]["hits"]

    if not hits:
        return ResultadoConsultaProcesso(
            atualizacoes=[],
            data_ultima_atualizacao_fonte=None,
        )

    source = hits[0]["_source"]

    data_ultima_atualizacao_fonte = None

    if source.get("dataHoraUltimaAtualizacao"):
        data_ultima_atualizacao_fonte = datetime.fromisoformat(
            source["dataHoraUltimaAtualizacao"].replace(
                "Z",
                "+00:00",
            )
        )

    movimentos = source.get("movimentos", [])

    atualizacoes = []

    for movimento in movimentos:
        data_movimento = datetime.fromisoformat(
            movimento["dataHora"].replace(
                "Z",
                "+00:00",
            )
        )

        if data_movimento.date() < data_base:
            continue

        atualizacao = AtualizacaoProcesso(
            codigo=movimento["codigo"],
            descricao=movimento["nome"],
            data_movimentacao=data_movimento,
            orgao_julgador=movimento.get(
                "orgaoJulgador",
                {},
            ).get("nome"),
        )

        atualizacoes.append(atualizacao)

    atualizacoes.sort(
        key=lambda x: x.data_movimentacao
    )

    return ResultadoConsultaProcesso(
        atualizacoes=atualizacoes,
        data_ultima_atualizacao_fonte=(
            data_ultima_atualizacao_fonte
        ),
    )