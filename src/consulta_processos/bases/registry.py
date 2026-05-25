import os

from dotenv import load_dotenv

from consulta_processos.bases.datajud import DataJudBaseClient
from consulta_processos.bases.esaj import ESAJClient
from consulta_processos.bases.eproc import EprocClient

load_dotenv()

BASES_DISPONIVEIS = {
    "esaj_tjsp": lambda: ESAJClient("tjsp"),
    "esaj_tjam": lambda: ESAJClient("tjam"),
    "eproc_jfrj": lambda: EprocClient("jfrj"),
    "eproc_trf2": lambda: EprocClient("trf2"),
    "eproc_jfes": lambda: EprocClient("jfes"),
    "datajud_tjrj": lambda: DataJudBaseClient("tjrj", os.getenv("DATAJUD_API_KEY", "")),
    "datajud_tjsp": lambda: DataJudBaseClient("tjsp", os.getenv("DATAJUD_API_KEY", "")),
    "datajud_tjes": lambda: DataJudBaseClient("tjes", os.getenv("DATAJUD_API_KEY", "")),
    "datajud_tjba": lambda: DataJudBaseClient("tjba", os.getenv("DATAJUD_API_KEY", "")),
    "datajud_tjam": lambda: DataJudBaseClient("tjam", os.getenv("DATAJUD_API_KEY", "")),
    "datajud_trf2": lambda: DataJudBaseClient("trf2", os.getenv("DATAJUD_API_KEY", "")),
}


def obter_client(base: str):
    base = base.lower()

    if base not in BASES_DISPONIVEIS:
        raise ValueError(
            f"Base não suportada: {base}"
        )

    return BASES_DISPONIVEIS[base]()


def consultar_processo(
    numero_processo: str,
    base: str,
):
    client = obter_client(base)

    return client.consultar(numero_processo)