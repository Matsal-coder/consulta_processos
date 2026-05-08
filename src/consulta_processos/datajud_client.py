import requests
from requests import RequestException

from consulta_processos.exceptions import FonteExternaError


DATAJUD_ENDPOINTS = {
    "tjrj": "https://api-publica.datajud.cnj.jus.br/api_publica_tjrj/_search",
}


class DataJudClient:
    def __init__(self, api_key: str, timeout: int = 30) -> None:
        self.api_key = api_key
        self.timeout = timeout

    def buscar_processo(
        self,
        tribunal: str,
        numero_processo: str,
    ) -> dict:
        endpoint = DATAJUD_ENDPOINTS[tribunal]

        numero_limpo = self._limpar_numero_processo(numero_processo)

        headers = {
            "Authorization": f"APIKey {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "query": {
                "match": {
                    "numeroProcesso": numero_limpo,
                }
            }
        }

        try:
            response = requests.post(
                endpoint,
                headers=headers,
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except RequestException as exc:
            raise FonteExternaError("Erro ao consultar a API pública do DataJud.") from exc

    @staticmethod
    def _limpar_numero_processo(numero_processo: str) -> str:
        return numero_processo.replace(".", "").replace("-", "")