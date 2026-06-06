from dataclasses import dataclass
from typing import Callable

from consulta_processos.bases.base import BaseConsultaProcessual
from consulta_processos.bases.datajud import DataJudBaseClient
from consulta_processos.bases.eproc import EprocClient
from consulta_processos.bases.esaj import ESAJClient
from consulta_processos.settings import get_settings


@dataclass(frozen=True)
class FonteProcessualConfig:
    key: str
    label: str
    sistema: str
    tribunal: str
    factory: Callable[[], BaseConsultaProcessual]
    ativa: bool = True
    observacao: str | None = None


FONTES_PROCESSUAIS = {
    "esaj_tjsp": FonteProcessualConfig(
        key="esaj_tjsp",
        label="TJSP - e-SAJ",
        sistema="esaj",
        tribunal="tjsp",
        factory=lambda: ESAJClient("tjsp"),
    ),
    "esaj_tjam": FonteProcessualConfig(
        key="esaj_tjam",
        label="TJAM - e-SAJ",
        sistema="esaj",
        tribunal="tjam",
        factory=lambda: ESAJClient("tjam"),
    ),
    "eproc_jfrj": FonteProcessualConfig(
        key="eproc_jfrj",
        label="JFRJ - eproc",
        sistema="eproc",
        tribunal="jfrj",
        factory=lambda: EprocClient("jfrj"),
    ),
    "eproc_trf2": FonteProcessualConfig(
        key="eproc_trf2",
        label="TRF2 - eproc",
        sistema="eproc",
        tribunal="trf2",
        factory=lambda: EprocClient("trf2"),
    ),
    "eproc_jfes": FonteProcessualConfig(
        key="eproc_jfes",
        label="JFES - eproc",
        sistema="eproc",
        tribunal="jfes",
        factory=lambda: EprocClient("jfes"),
    ),
    "eproc_tjrj": FonteProcessualConfig(
        key="eproc_tjrj",
        label="TJRJ - eproc",
        sistema="eproc",
        tribunal="tjrj",
        factory=lambda: EprocClient("tjrj"),
        observacao="Pode exigir captcha.",
    ),
    "datajud_tjrj": FonteProcessualConfig(
        key="datajud_tjrj",
        label="TJRJ - DataJud",
        sistema="datajud",
        tribunal="tjrj",
        factory=lambda: DataJudBaseClient(
            tribunal="tjrj",
            api_key=get_settings().datajud_api_key,
        ),
    ),
    "datajud_tjsp": FonteProcessualConfig(
        key="datajud_tjsp",
        label="TJSP - DataJud",
        sistema="datajud",
        tribunal="tjsp",
        factory=lambda: DataJudBaseClient(
            tribunal="tjsp",
            api_key=get_settings().datajud_api_key,
        ),
    ),
    "datajud_tjes": FonteProcessualConfig(
        key="datajud_tjes",
        label="TJES - DataJud",
        sistema="datajud",
        tribunal="tjes",
        factory=lambda: DataJudBaseClient(
            tribunal="tjes",
            api_key=get_settings().datajud_api_key,
        ),
    ),
    "datajud_tjba": FonteProcessualConfig(
        key="datajud_tjba",
        label="TJBA - DataJud",
        sistema="datajud",
        tribunal="tjba",
        factory=lambda: DataJudBaseClient(
            tribunal="tjba",
            api_key=get_settings().datajud_api_key,
        ),
    ),
    "datajud_tjam": FonteProcessualConfig(
        key="datajud_tjam",
        label="TJAM - DataJud",
        sistema="datajud",
        tribunal="tjam",
        factory=lambda: DataJudBaseClient(
            tribunal="tjam",
            api_key=get_settings().datajud_api_key,
        ),
    ),
    "datajud_trf2": FonteProcessualConfig(
        key="datajud_trf2",
        label="TRF2 - DataJud",
        sistema="datajud",
        tribunal="trf2",
        factory=lambda: DataJudBaseClient(
            tribunal="trf2",
            api_key=get_settings().datajud_api_key,
        ),
    ),
}