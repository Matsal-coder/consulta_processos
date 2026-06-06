from datetime import date, datetime, timezone

from consulta_processos.bases.base import (
    MovimentoProcessual,
    ResultadoConsultaProcessual,
)
from consulta_processos.models import ConsultaInput
from consulta_processos.services.consulta_service import consultar_processos


def test_consultar_processos(monkeypatch):

    def fake_consultar_atualizacoes_por_base(
        numero_processo: str,
        base: str,
        data_base: date,
    ):
        assert numero_processo == "0964024-67.2024.8.19.0001"
        assert base == "datajud_tjrj"
        assert data_base == date(2025, 1, 1)

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
        "consulta_processos.services.consulta_service.consultar_atualizacoes_por_base",
        fake_consultar_atualizacoes_por_base,
    )

    payload = ConsultaInput.model_validate(
        {
            "processos": [
                {
                    "numero_processo": "0964024-67.2024.8.19.0001",
                    "base": "datajud_tjrj",
                    "data_base": "2025-01-01",
                }
            ]
        }
    )

    resultado = consultar_processos(payload)

    assert len(resultado.processos) == 1

    processo = resultado.processos[0]

    assert processo.numero_processo == "0964024-67.2024.8.19.0001"
    assert processo.base == "datajud_tjrj"
    assert processo.fonte == "DataJud/TJRJ"
    assert len(processo.atualizacoes) == 1
    assert processo.atualizacoes[0].descricao == "Publicação"

    assert (
        processo.data_ultima_atualizacao_fonte
        == datetime(2026, 3, 10, 14, 40, tzinfo=timezone.utc)
    )

    assert processo.observacao is not None