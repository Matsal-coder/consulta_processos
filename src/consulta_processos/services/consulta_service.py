from __future__ import annotations

import logging
from datetime import date

from consulta_processos.bases.base import ResultadoConsultaProcessual
from consulta_processos.bases.registry import consultar_processo
from consulta_processos.models import (
    AtualizacaoProcesso,
    ConsultaInput,
    ConsultaResultado,
    ProcessoResultado,
)
from consulta_processos.utils.dates import parse_date, parse_datetime

logger = logging.getLogger(__name__)


def _montar_observacao(fonte: str) -> str | None:
    if fonte.lower().startswith("datajud"):
        return "A fonte DataJud pode ter defasagem em relação ao sistema original do tribunal."

    return None


def _data_movimento_maior_ou_igual(
    data_movimento: str | None,
    data_base: date,
) -> bool:
    data_convertida = parse_date(data_movimento)

    if not data_convertida:
        return False

    return data_convertida >= data_base


def consultar_atualizacoes_por_base(
    numero_processo: str,
    base: str,
    data_base: date,
) -> ResultadoConsultaProcessual:
    resultado = consultar_processo(
        numero_processo=numero_processo,
        base=base,
    )

    resultado.movimentos = [
        movimento
        for movimento in resultado.movimentos
        if _data_movimento_maior_ou_igual(
            movimento.data,
            data_base,
        )
    ]

    return resultado


def consultar_processos(payload: ConsultaInput) -> ConsultaResultado:
    resultados = []

    logger.info(
        "Iniciando consulta de %s processo(s)",
        len(payload.processos),
    )

    for processo in payload.processos:
        logger.info(
            "Consultando processo %s na base %s",
            processo.numero_processo,
            processo.base,
        )
        resultado_consulta = consultar_atualizacoes_por_base(
            numero_processo=processo.numero_processo,
            base=processo.base,
            data_base=processo.data_base,
        )

        atualizacoes = [
            AtualizacaoProcesso(
                codigo=0,
                descricao=movimento.descricao,
                data_movimentacao=parse_datetime(movimento.data),
                orgao_julgador=None,
            )
            for movimento in resultado_consulta.movimentos
        ]

        resultados.append(
            ProcessoResultado(
                numero_processo=processo.numero_processo,
                base=processo.base,
                fonte=resultado_consulta.fonte,
                data_ultima_atualizacao_fonte=(resultado_consulta.data_ultima_atualizacao_fonte),
                observacao=_montar_observacao(resultado_consulta.fonte),
                atualizacoes=atualizacoes,
            )
        )
        logger.info(
            "Consulta concluída para processo %s na base %s com %s movimentação(ões)",
            processo.numero_processo,
            processo.base,
            len(resultado_consulta.movimentos),
        )

    return ConsultaResultado(processos=resultados)
