import os

from consulta_processos.models import (
    ConsultaInput,
    ConsultaResultado,
    ProcessoResultado,
)
from consulta_processos.scrapers.datajud_tjrj import consultar_processo_datajud_tjrj


def consultar_processos(payload: ConsultaInput) -> ConsultaResultado:
    resultados = []

    api_key = os.environ["DATAJUD_API_KEY"]

    for processo in payload.processos:
        if processo.base == "tjrj_datajud":
            atualizacoes = consultar_processo_datajud_tjrj(
                numero_processo=processo.numero_processo,
                data_base=processo.data_base,
                api_key=api_key,
            )
        else:
            raise ValueError(f"Base ainda não suportada: {processo.base}")

        resultados.append(
            ProcessoResultado(
                numero_processo=processo.numero_processo,
                base=processo.base,
                atualizacoes=atualizacoes,
            )
        )

    return ConsultaResultado(processos=resultados)