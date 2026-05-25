from consulta_processos.bases.catalog import FONTES_PROCESSUAIS


def obter_client(base: str):
    base = base.lower()

    if base not in FONTES_PROCESSUAIS:
        raise ValueError(f"Base não suportada: {base}")

    return FONTES_PROCESSUAIS[base].factory()


def consultar_processo(numero_processo: str, base: str):
    client = obter_client(base)
    return client.consultar(numero_processo)