import os

from consulta_processos.models import (
    ConsultaInput,
    ConsultaResultado,
    ProcessoResultado,
)
from consulta_processos.scrapers.datajud_tjrj import consultar_processo_datajud_tjrj
from consulta_processos.exceptions import BaseNaoSuportadaError, ConfiguracaoError
from dotenv import load_dotenv

load_dotenv()

def consultar_processos(payload: ConsultaInput) -> ConsultaResultado:
    resultados = []
    api_key = os.getenv("DATAJUD_API_KEY")

    if not api_key:
        raise ConfiguracaoError("Variável de ambiente DATAJUD_API_KEY não configurada.")

    for processo in payload.processos:
        if processo.base == "tjrj_datajud":
            resultado_consulta = consultar_processo_datajud_tjrj(
                numero_processo=processo.numero_processo,
                data_base=processo.data_base,
                api_key=api_key,
            )
        else:
            raise BaseNaoSuportadaError(f"Base ainda não suportada: {processo.base}")

        resultados.append(
            ProcessoResultado(
                numero_processo=processo.numero_processo,
                base=processo.base,
                fonte="datajud",
                data_ultima_atualizacao_fonte=(
                    resultado_consulta.data_ultima_atualizacao_fonte
                ),
                observacao=(
                    "A fonte DataJud pode ter defasagem em relação "
                    "ao sistema original do tribunal."
                ),
                atualizacoes=resultado_consulta.atualizacoes,
            )
        )

    return ConsultaResultado(processos=resultados)