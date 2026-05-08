from datetime import date, datetime

from consulta_processos.datajud_client import DataJudClient
from consulta_processos.models import AtualizacaoProcesso


def consultar_processo_datajud_tjrj(
    numero_processo: str,
    data_base: date,
    api_key: str,
) -> list[AtualizacaoProcesso]:
    client = DataJudClient(api_key=api_key)

    data = client.buscar_processo(
        tribunal="tjrj",
        numero_processo=numero_processo,
    )

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

        atualizacoes.append(
            AtualizacaoProcesso(
                codigo=movimento["codigo"],
                descricao=movimento["nome"],
                data_movimentacao=data_movimento,
                orgao_julgador=movimento.get("orgaoJulgador", {}).get("nome"),
            )
        )

    atualizacoes.sort(key=lambda x: x.data_movimentacao)

    return atualizacoes