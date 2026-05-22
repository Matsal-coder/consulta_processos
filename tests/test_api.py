from datetime import date, datetime, timezone

from fastapi.testclient import TestClient

from consulta_processos.api import app
from consulta_processos.bases.base import (
    MovimentoProcessual,
    ResultadoConsultaProcessual,
)


client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_consultar_processos(monkeypatch):

    def fake_consultar_atualizacoes_por_base(
        numero_processo: str,
        base: str,
        data_base: date,
    ):
        return ResultadoConsultaProcessual(
            numero_processo=numero_processo,
            tribunal="tjrj",
            sistema="DataJud",
            fonte="DataJud/TJRJ",
            url=None,
            movimentos=[
                MovimentoProcessual(
                    data="2025-01-23T00:00:00+00:00",
                    descricao="Publicação",
                    fonte="DataJud/TJRJ",
                )
            ],
            data_ultima_atualizacao_fonte=datetime(
                2026,
                3,
                10,
                14,
                40,
                tzinfo=timezone.utc,
            ),
            erro=None,
        )

    monkeypatch.setattr(
        "consulta_processos.services.consultar_atualizacoes_por_base",
        fake_consultar_atualizacoes_por_base,
    )

    response = client.post(
        "/consultar-processos",
        json={
            "processos": [
                {
                    "numero_processo": "0964024-67.2024.8.19.0001",
                    "base": "datajud_tjrj",
                    "data_base": "2025-01-01",
                }
            ]
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["processos"]) == 1

    processo = data["processos"][0]

    assert processo["numero_processo"] == "0964024-67.2024.8.19.0001"
    assert processo["base"] == "datajud_tjrj"
    assert processo["fonte"] == "DataJud/TJRJ"

    assert len(processo["atualizacoes"]) == 1

    assert (
        processo["atualizacoes"][0]["descricao"]
        == "Publicação"
    )