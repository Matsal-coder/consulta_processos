from __future__ import annotations

from datetime import date, datetime

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
    if not data_movimento:
        return False

    data_convertida = _parse_data_movimento(data_movimento)

    if not data_convertida:
        return False

    return data_convertida >= data_base


def _parse_data_movimento(
    data_movimento: str,
) -> date | None:
    formatos = [
        "%d/%m/%Y",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S%z",
    ]

    for formato in formatos:
        try:
            return datetime.strptime(
                data_movimento,
                formato,
            ).date()
        except ValueError:
            continue

    return None