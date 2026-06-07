from __future__ import annotations

import logging

from bs4 import BeautifulSoup
from selenium.common.exceptions import UnexpectedAlertPresentException
from seleniumbase import Driver

from consulta_processos.bases.base import (
    BaseConsultaProcessual,
    MovimentoProcessual,
    ResultadoConsultaProcessual,
)
from consulta_processos.exceptions import (
    BaseNaoSuportadaError,
)

logger = logging.getLogger(__name__)

class EprocClient(BaseConsultaProcessual):
    nome = "eproc"

    BASE_URLS = {
        "jfrj": "https://eproc.jfrj.jus.br/eproc",
        "trf2": "https://eproc.trf2.jus.br/eproc",
        "jfes": "https://eproc.jfes.jus.br/eproc",
        "tjrj": "https://eproc1g-cp.tjrj.jus.br/eproc",
    }

    def __init__(
        self,
        tribunal: str,
        headless: bool = True,
        salvar_debug_html: bool = False,
    ):
        tribunal = tribunal.lower()

        if tribunal not in self.BASE_URLS:
            raise BaseNaoSuportadaError(
                f"Tribunal eproc não suportado: {tribunal}"
            )

        self.tribunal = tribunal
        self.base_url = self.BASE_URLS[tribunal]
        self.headless = headless
        self.salvar_debug_html = salvar_debug_html

    def _build_url(self) -> str:
        return (
            f"{self.base_url}/externo_controlador.php"
            "?acao=processo_consulta_publica"
            "&acao_origem=processo_consulta_publica"
        )

    def consultar(
        self,
        numero_processo: str,
    ) -> ResultadoConsultaProcessual:
        url = self._build_url()
        driver = None

        try:
            driver = Driver(
                browser="chrome",
                headless=self.headless,
                uc=True,
            )

            driver.get(url)
            driver.sleep(5)

            driver.type(
                "input[id^='txtNum']",
                numero_processo,
            )


            driver.click("button#sbmNovo")
            driver.sleep(5)

            html = driver.page_source

            if self.salvar_debug_html:
                self._salvar_debug_html(html)

            if self._tem_bloqueio(html):
                return ResultadoConsultaProcessual(
                    numero_processo=numero_processo,
                    tribunal=self.tribunal,
                    sistema="eproc",
                    fonte=f"eproc/{self.tribunal.upper()}",
                    url=driver.current_url,
                    movimentos=[],
                    erro=(
                        "Consulta eproc bloqueada ou protegida "
                        "por validação do site."
                    ),
                )

            movimentos = self._parse_movimentos(html)

            return ResultadoConsultaProcessual(
                numero_processo=numero_processo,
                tribunal=self.tribunal,
                sistema="eproc",
                fonte=f"eproc/{self.tribunal.upper()}",
                url=driver.current_url,
                movimentos=movimentos,
                erro=None,
            )
        
        except UnexpectedAlertPresentException as exc:
            alerta = self._obter_texto_alerta(driver)

            return ResultadoConsultaProcessual(
                numero_processo=numero_processo,
                tribunal=self.tribunal,
                sistema="eproc",
                fonte=f"eproc/{self.tribunal.upper()}",
                url=driver.current_url if driver else url,
                movimentos=[],
                erro=(
                    "Consulta eproc bloqueada por alerta/validação do site. "
                    f"Mensagem: {alerta or str(exc)}"
                ),
            )
        
        except Exception as exc:
            logger.exception(
                "Erro ao consultar processo %s no eproc %s",
                numero_processo,
                self.tribunal,
            )
            return ResultadoConsultaProcessual(
                numero_processo=numero_processo,
                tribunal=self.tribunal,
                sistema="eproc",
                fonte=f"eproc/{self.tribunal.upper()}",
                url=url,
                movimentos=[],
                erro=str(exc),
            )

        finally:
            if driver:
                driver.quit()

    def _obter_texto_alerta(self, driver) -> str | None:
        if not driver:
            return None

        try:
            alert = driver.switch_to.alert
            texto = alert.text
            alert.accept()
            return texto
        except Exception:
            return None

    def _parse_movimentos(
        self,
        html: str,
    ) -> list[MovimentoProcessual]:
        soup = BeautifulSoup(html, "html.parser")

        tabelas = soup.select("table.infraTable")

        tabela_movimentos = None

        for tabela in tabelas:
            headers = [
                th.get_text(" ", strip=True)
                for th in tabela.select("th")
            ]

            if (
                "Evento" in headers
                and "Data/Hora" in headers
                and "Descrição" in headers
            ):
                tabela_movimentos = tabela
                break

        if tabela_movimentos is None:
            return []

        movimentos = []

        for row in tabela_movimentos.select("tr")[1:]:
            cols = row.select("td")

            if len(cols) < 3:
                continue

            evento = cols[0].get_text(" ", strip=True)
            data_hora = cols[1].get_text(" ", strip=True)
            descricao = cols[2].get_text(" ", strip=True)

            if evento:
                descricao = f"Evento {evento} - {descricao}"

            movimentos.append(
                MovimentoProcessual(
                    data=data_hora,
                    descricao=" ".join(descricao.split()),
                    fonte=f"eproc/{self.tribunal.upper()}",
                )
            )

        return movimentos

    def _tem_bloqueio(self, html: str) -> bool:
        html_lower = html.lower()

        indicadores = [
            "cloudflare",
            "não foi possível conectar ao site",
            "captcha",
            "turnstile",
            "cf-challenge",
        ]

        return any(
            indicador in html_lower
            for indicador in indicadores
        )

    def _salvar_debug_html(self, html: str) -> None:
        caminho = f"debug_eproc_{self.tribunal}.html"

        with open(
            caminho,
            "w",
            encoding="utf-8",
        ) as f:
            f.write(html)