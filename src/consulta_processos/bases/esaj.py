from __future__ import annotations

from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup

@dataclass
class MovimentoProcessual:
    data: str | None
    descricao: str
    fonte: str = "e-SAJ"


@dataclass
class ResultadoESAJ:
    numero_processo: str
    tribunal: str
    sistema: str
    url: str
    movimentos: list[MovimentoProcessual]
    erro: str | None = None


class ESAJClient:
    BASE_URLS = {
        "tjsp": "https://esaj.tjsp.jus.br",
        "tjam": "https://consultasaj.tjam.jus.br",
    }

    def __init__(self, tribunal: str):
        tribunal = tribunal.lower()

        if tribunal not in self.BASE_URLS:
            raise ValueError(
                f"Tribunal e-SAJ não suportado: {tribunal}"
            )

        self.tribunal = tribunal
        self.base_url = self.BASE_URLS[tribunal]

    def _build_url(self) -> str:
        return f"{self.base_url}/cpopg/search.do"
    
    def _parse_movimentos(
        self,
        html: str,
    ) -> list[MovimentoProcessual]:

        soup = BeautifulSoup(html, "html.parser")

        rows = soup.select(
            "#tabelaUltimasMovimentacoes tr"
        )

        movimentos = []

        for row in rows:

            data_tag = row.select_one(
                ".dataMovimentacao"
            )

            descricao_tag = row.select_one(
                ".descricaoMovimentacao"
            )

            if not descricao_tag:
                continue

            data = (
                data_tag.get_text(strip=True)
                if data_tag
                else None
            )

            descricao = " ".join(
                descricao_tag.get_text(
                    " ",
                    strip=True,
                ).split()
            )

            movimentos.append(
                MovimentoProcessual(
                    data=data,
                    descricao=descricao,
                )
            )

        return movimentos

    def consultar(
        self,
        numero_processo: str,
    ) -> ResultadoESAJ:

        session = requests.Session()

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0 Safari/537.36"
            ),
            "Referer": f"{self.base_url}/cpopg/open.do",
        }

        open_url = f"{self.base_url}/cpopg/open.do"
        show_url = self._build_url()

        params = {
            "conversationId": "",
            "cbPesquisa": "NUMPROC",
            "dadosConsulta.valorConsultaNuUnificado": numero_processo,
            "dadosConsulta.valorConsultaNuUnificadoInput": numero_processo,
            "dadosConsulta.valorConsulta": "",
            "dadosConsulta.tipoNuProcesso": "UNIFICADO",
        }

        try:
            session.get(
                open_url,
                headers=headers,
                timeout=30,
            )

            response = session.get(
                show_url,
                params=params,
                headers=headers,
                timeout=30,
            )

            response.raise_for_status()

        except requests.RequestException as exc:
            return ResultadoESAJ(
                numero_processo=numero_processo,
                tribunal=self.tribunal,
                sistema="e-SAJ",
                url=show_url,
                movimentos=[],
                erro=str(exc),
            )

        with open(
            "debug_esaj_response.html",
            "w",
            encoding="utf-8",
        ) as f:
            f.write(response.text)

        movimentos = self._parse_movimentos(
            response.text
        )

        return ResultadoESAJ(
            numero_processo=numero_processo,
            tribunal=self.tribunal,
            sistema="e-SAJ",
            url=response.url,
            movimentos=movimentos,
            erro=None,
        )