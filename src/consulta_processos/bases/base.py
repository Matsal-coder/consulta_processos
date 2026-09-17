from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass
class MovimentoProcessual:
    data: str | None
    descricao: str
    fonte: str


@dataclass
class ResultadoConsultaProcessual:
    numero_processo: str
    tribunal: str
    sistema: str
    fonte: str
    url: str | None
    movimentos: list[MovimentoProcessual]
    data_ultima_atualizacao_fonte: datetime | None = None
    erro: str | None = None


class BaseConsultaProcessual(ABC):
    nome: str

    @abstractmethod
    def consultar(
        self,
        numero_processo: str,
    ) -> ResultadoConsultaProcessual:
        pass
