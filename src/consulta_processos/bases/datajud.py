from __future__ import annotations

from datetime import datetime

from consulta_processos.bases.base import (
    BaseConsultaProcessual,
    MovimentoProcessual,
    ResultadoConsultaProcessual,
)
from consulta_processos.datajud_client import DataJudClient
from consulta_processos.exceptions import FonteExternaError


class DataJudBaseClient(BaseConsultaProcessual):
    nome = "datajud"

    def __init__(
        self,
        tribunal: str,
        api_key: str,
    ) -> None:
        self.tribunal = tribunal.lower()
        self.api_key = api_key
        self.client = DataJudClient(api_key=api_key)

    def _get_source(self, data: dict) -> dict:
        hits = data.get("hits", {}).get("hits", [])

        if not hits:
            return {}

        return hits[0].get("_source", {})

    def _parse_data_ultima_atualizacao_fonte(
        self,
        source: dict,
    ) -> datetime | None:
        data_raw = source.get("dataHoraUltimaAtualizacao")

        if not data_raw:
            return None

        return datetime.fromisoformat(data_raw.replace("Z", "+00:00"))

    def consultar(
        self,
        numero_processo: str,
    ) -> ResultadoConsultaProcessual:
        try:
            data = self.client.buscar_processo(
                tribunal=self.tribunal,
                numero_processo=numero_processo,
            )
        except FonteExternaError as exc:
            return ResultadoConsultaProcessual(
                numero_processo=numero_processo,
                tribunal=self.tribunal,
                sistema="DataJud",
                fonte=f"DataJud/{self.tribunal.upper()}",
                url=None,
                movimentos=[],
                erro=str(exc),
            )

        source = self._get_source(data)

        data_ultima_atualizacao_fonte = self._parse_data_ultima_atualizacao_fonte(source)

        movimentos = self._parse_movimentos(source)

        return ResultadoConsultaProcessual(
            numero_processo=numero_processo,
            tribunal=self.tribunal,
            sistema="DataJud",
            fonte=f"DataJud/{self.tribunal.upper()}",
            url=None,
            movimentos=movimentos,
            data_ultima_atualizacao_fonte=data_ultima_atualizacao_fonte,
            erro=None,
        )

    def _parse_movimentos(
        self,
        source: dict,
    ) -> list[MovimentoProcessual]:
        movimentos_raw = source.get("movimentos", [])
        # hits = data.get("hits", {}).get("hits", [])

        # if not hits:
        #     return []

        # source = hits[0].get("_source", {})
        # movimentos_raw = source.get("movimentos", [])

        movimentos = []

        for mov in movimentos_raw:
            data_movimento = mov.get("dataHora") or mov.get("dataMovimento") or mov.get("data")

            descricao = (
                mov.get("nome") or mov.get("descricao") or mov.get("complementoTabelado") or ""
            )

            complemento = mov.get("complementoTabelado")

            if complemento and complemento not in descricao:
                descricao = f"{descricao} {complemento}"

            descricao = " ".join(descricao.split())

            if not descricao:
                continue

            movimentos.append(
                MovimentoProcessual(
                    data=data_movimento,
                    descricao=descricao,
                    fonte=f"DataJud/{self.tribunal.upper()}",
                )
            )

        return movimentos
