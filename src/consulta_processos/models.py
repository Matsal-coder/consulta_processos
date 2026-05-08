from datetime import date, datetime
from typing import Literal
from pydantic import BaseModel, Field


class ProcessoConsulta(BaseModel):
    numero_processo: str = Field(..., description="Número CNJ do processo")
    base: Literal["tjrj_datajud", "tjrj_eproc", "tjsp", "trf2", "djen"]
    data_base: date


class ConsultaInput(BaseModel):
    processos: list[ProcessoConsulta]


class AtualizacaoProcesso(BaseModel):
    codigo: int
    descricao: str
    data_movimentacao: datetime
    orgao_julgador: str | None = None


class ProcessoResultado(BaseModel):
    numero_processo: str
    base: str
    fonte: str
    data_ultima_atualizacao_fonte: datetime | None = None
    observacao: str | None = None
    atualizacoes: list[AtualizacaoProcesso]


class ConsultaResultado(BaseModel):
    processos: list[ProcessoResultado]

class ResultadoConsultaProcesso(BaseModel):
    atualizacoes: list[AtualizacaoProcesso]
    data_ultima_atualizacao_fonte: datetime | None = None