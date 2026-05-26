from datetime import date, datetime
from pydantic import BaseModel, field_validator

from consulta_processos.bases.catalog import (
    FONTES_PROCESSUAIS,
)


class ProcessoConsulta(BaseModel):
    numero_processo: str
    base: str
    data_base: date

    @field_validator("base")
    @classmethod
    def validar_base(cls, value: str) -> str:
        value = value.lower()

        if value not in FONTES_PROCESSUAIS:
            raise ValueError(
                f"Base não suportada: {value}"
            )

        return value


class ConsultaInput(BaseModel):
    processos: list[ProcessoConsulta]


class AtualizacaoProcesso(BaseModel):
    codigo: int
    descricao: str
    data_movimentacao: datetime
    orgao_julgador: str | None = None
    nova: bool | None = None    


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