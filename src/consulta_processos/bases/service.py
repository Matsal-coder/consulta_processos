from __future__ import annotations

from datetime import date
from consulta_processos.utils.dates import parse_date

from consulta_processos.bases.base import ResultadoConsultaProcessual
from consulta_processos.bases.registry import consultar_processo


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


def _data_movimento_maior_ou_igual(
    data_movimento: str | None,
    data_base: date,
) -> bool:
    data_convertida = parse_date(data_movimento)

    if not data_convertida:
        return False

    return data_convertida >= data_base
