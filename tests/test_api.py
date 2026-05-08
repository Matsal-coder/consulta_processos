from datetime import datetime, timezone

from fastapi.testclient import TestClient

from consulta_processos.api import app
from consulta_processos.models import AtualizacaoProcesso, ResultadoConsultaProcesso


client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_consultar_processos(monkeypatch):
    monkeypatch.setenv("DATAJUD_API_KEY", "fake-api-key")

    def fake_consultar_processo_datajud_tjrj(
        numero_processo,
        data_base,
        api_key,
    ):
        return ResultadoConsultaProcesso(
            data_ultima_atualizacao_fonte=datetime(
                2026,
                3,
                10,
                14,
                40,
                tzinfo=timezone.utc,
            ),
            atualizacoes=[
                AtualizacaoProcesso(
                    codigo=92,
                    descricao="Publicação",
                    data_movimentacao=datetime(
                        2025,
                        1,
                        23,
                        tzinfo=timezone.utc,
                    ),
                    orgao_julgador="7ª Vara da Fazenda Pública da Comarca da Capital",
                )
            ],
        )

    monkeypatch.setattr(
        "consulta_processos.services.consultar_processo_datajud_tjrj",
        fake_consultar_processo_datajud_tjrj,
    )

    response = client.post(
        "/consultar-processos",
        json={
            "processos": [
                {
                    "numero_processo": "0964024-67.2024.8.19.0001",
                    "base": "tjrj_datajud",
                    "data_base": "2025-01-01",
                }
            ]
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["processos"]) == 1
    assert data["processos"][0]["numero_processo"] == "0964024-67.2024.8.19.0001"
    assert data["processos"][0]["base"] == "tjrj_datajud"
    assert data["processos"][0]["fonte"] == "datajud"
    assert len(data["processos"][0]["atualizacoes"]) == 1
    assert data["processos"][0]["atualizacoes"][0]["descricao"] == "Publicação"