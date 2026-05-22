from datetime import datetime

from consulta_processos.bases.service import consultar_atualizacoes_por_base
from consulta_processos.models import (
    AtualizacaoProcesso,
    ConsultaInput,
    ConsultaResultado,
    ProcessoResultado,
)


def consultar_processos(payload: ConsultaInput) -> ConsultaResultado:
    resultados = []

    for processo in payload.processos:
        resultado_consulta = consultar_atualizacoes_por_base(
            numero_processo=processo.numero_processo,
            base=processo.base,
            data_base=processo.data_base,
        )

        atualizacoes = [
            AtualizacaoProcesso(
                codigo=0,
                descricao=movimento.descricao,
                data_movimentacao=_parse_datetime_movimento(
                    movimento.data
                ),
                orgao_julgador=None,
            )
            for movimento in resultado_consulta.movimentos
        ]

        resultados.append(
            ProcessoResultado(
                numero_processo=processo.numero_processo,
                base=processo.base,
                fonte=resultado_consulta.fonte,
                data_ultima_atualizacao_fonte=(
                    resultado_consulta.data_ultima_atualizacao_fonte
                ),
                observacao=_montar_observacao(resultado_consulta.fonte),
                atualizacoes=atualizacoes,
            )
        )

    return ConsultaResultado(processos=resultados)


def _parse_datetime_movimento(data_movimento: str | None) -> datetime | None:
    if not data_movimento:
        return None

    formatos = [
        "%d/%m/%Y",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S%z",
    ]

    for formato in formatos:
        try:
            return datetime.strptime(data_movimento, formato)
        except ValueError:
            continue

    return None


def _montar_observacao(fonte: str) -> str | None:
    if fonte.lower().startswith("datajud"):
        return (
            "A fonte DataJud pode ter defasagem em relação "
            "ao sistema original do tribunal."
        )

    return None