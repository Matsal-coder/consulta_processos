from __future__ import annotations

import requests

from consulta_processos.bases.base import (
    BaseConsultaProcessual,
    MovimentoProcessual,
    ResultadoConsultaProcessual,
)


class EprocClient(BaseConsultaProcessual):
    nome = "eproc"

    BASE_URLS = {
        "jfrj": "https://eproc.jfrj.jus.br/eproc",
        "trf2": "https://eproc.trf2.jus.br/eproc",
        "jfes": "https://eproc.jfes.jus.br/eproc",
    }

    def __init__(self, tribunal: str):
        tribunal = tribunal.lower()

        if tribunal not in self.BASE_URLS:
            raise ValueError(
                f"Tribunal eproc não suportado: {tribunal}"
            )

        self.tribunal = tribunal
        self.base_url = self.BASE_URLS[tribunal]

    def _build_url(self) -> str:
        return (
            f"{self.base_url}/externo_controlador.php"
        )

    def consultar(
        self,
        numero_processo: str,
    ) -> ResultadoConsultaProcessual:

        url = self._build_url()

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0 Safari/537.36"
            ),
        }

        params = {
            "acao": "processo_consulta_publica",
            "acao_origem": "processo_consulta_publica",
        }

        try:
            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=30,
            )

            response.raise_for_status()

        except requests.RequestException as exc:
            return ResultadoConsultaProcessual(
                numero_processo=numero_processo,
                tribunal=self.tribunal,
                sistema="eproc",
                fonte=f"eproc/{self.tribunal.upper()}",
                url=url,
                movimentos=[],
                erro=str(exc),
            )

        with open(
            "debug_eproc_response.html",
            "w",
            encoding="utf-8",
        ) as f:
            f.write(response.text)
        
        if "Não foi possível conectar ao site" in response.text or "cloudflare" in response.text.lower():
            return ResultadoConsultaProcessual(
                numero_processo=numero_processo,
                tribunal=self.tribunal,
                sistema="eproc",
                fonte=f"eproc/{self.tribunal.upper()}",
                url=response.url,
                movimentos=[],
                erro=(
                    "Consulta eproc bloqueada/indisponível por proteção Cloudflare "
                    "ou validação do site."
                ),
            )

        return ResultadoConsultaProcessual(
            numero_processo=numero_processo,
            tribunal=self.tribunal,
            sistema="eproc",
            fonte=f"eproc/{self.tribunal.upper()}",
            url=response.url,
            movimentos=[],
            erro=None,
        )