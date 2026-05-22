from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


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
    erro: str | None = None


class BaseConsultaProcessual(ABC):
    nome: str

    @abstractmethod
    def consultar(
        self,
        numero_processo: str,
    ) -> ResultadoConsultaProcessual:
        pass