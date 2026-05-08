from datetime import date
from pydantic import BaseModel, Field
from typing import Literal


class ProcessoConsulta(BaseModel):
    numero_processo: str = Field(
        ...,
        description="Número CNJ do processo"
    )

    base: Literal[
        "tjsp",
        "tjrj",
        "trf2",
        "djen"
    ]

    data_base: date


class ConsultaInput(BaseModel):
    processos: list[ProcessoConsulta]


class AtualizacaoProcesso(BaseModel):
    data_movimentacao: date
    descricao: str


class ProcessoResultado(BaseModel):
    numero_processo: str
    base: str
    atualizacoes: list[AtualizacaoProcesso]


class ConsultaResultado(BaseModel):
    processos: list[ProcessoResultado]