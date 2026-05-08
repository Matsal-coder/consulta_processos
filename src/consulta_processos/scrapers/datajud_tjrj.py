from datetime import date, datetime

import requests

from consulta_processos.models import AtualizacaoProcesso


DATAJUD_TJRJ_URL = (
    "https://api-publica.datajud.cnj.jus.br/api_publica_tjrj/_search"
)


def consultar_processo_datajud_tjrj(
    numero_processo: str,
    data_base: date,
    api_key: str,
) -> list[AtualizacaoProcesso]:

    numero_limpo = (
        numero_processo
        .replace(".", "")
        .replace("-", "")
    )

    headers = {
        "Authorization": f"APIKey {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "query": {
            "match": {
                "numeroProcesso": numero_limpo
            }
        }
    }

    response = requests.post(
        DATAJUD_TJRJ_URL,
        headers=headers,
        json=payload,
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    hits = data["hits"]["hits"]

    if not hits:
        return []

    source = hits[0]["_source"]

    movimentos = source.get("movimentos", [])

    atualizacoes = []

    for movimento in movimentos:
        data_movimento = datetime.fromisoformat(
            movimento["dataHora"].replace("Z", "+00:00")
        )

        if data_movimento.date() < data_base:
            continue

        atualizacao = AtualizacaoProcesso(
            codigo=movimento["codigo"],
            descricao=movimento["nome"],
            data_movimentacao=data_movimento,
            orgao_julgador=movimento.get(
                "orgaoJulgador",
                {},
            ).get("nome"),
        )

        atualizacoes.append(atualizacao)

    atualizacoes.sort(
        key=lambda x: x.data_movimentacao
    )

    return atualizacoes