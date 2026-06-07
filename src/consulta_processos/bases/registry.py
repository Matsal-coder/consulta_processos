from consulta_processos.bases.catalog import FONTES_PROCESSUAIS
from consulta_processos.exceptions import (
    BaseNaoSuportadaError,
)


def obter_client(base: str):
    base = base.lower()

    if base not in FONTES_PROCESSUAIS:
        raise BaseNaoSuportadaError(
        f"Base não suportada: {base}"
    )

    return FONTES_PROCESSUAIS[base].factory()


def consultar_processo(numero_processo: str, base: str):
    client = obter_client(base)
    return client.consultar(numero_processo)