from datetime import date, datetime, timezone
from consulta_processos.models import (
    AtualizacaoProcesso,
    ConsultaInput,
    ResultadoConsultaProcesso,
)
from consulta_processos.services import consultar_processos
import pytest

def test_consultar_processos_com_base_tjrj_datajud(monkeypatch):
    monkeypatch.setenv("DATAJUD_API_KEY", "fake-api-key")

    def fake_consultar_processo_datajud_tjrj(
        numero_processo: str,
        data_base: date,
        api_key: str,
    ):
        assert numero_processo == "0964024-67.2024.8.19.0001"
        assert data_base == date(2025, 1, 1)
        assert api_key == "fake-api-key"

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
                    data_movimentacao=datetime(2025, 1, 23, tzinfo=timezone.utc),
                    orgao_julgador="7ª Vara da Fazenda Pública da Comarca da Capital",
                )
            ],
        )

    monkeypatch.setattr(
        "consulta_processos.services.consultar_processo_datajud_tjrj",
        fake_consultar_processo_datajud_tjrj,
    )

    payload = ConsultaInput.model_validate(
        {
            "processos": [
                {
                    "numero_processo": "0964024-67.2024.8.19.0001",
                    "base": "tjrj_datajud",
                    "data_base": "2025-01-01",
                }
            ]
        }
    )

    resultado = consultar_processos(payload)

    assert len(resultado.processos) == 1
    assert resultado.processos[0].numero_processo == "0964024-67.2024.8.19.0001"
    assert resultado.processos[0].base == "tjrj_datajud"
    assert len(resultado.processos[0].atualizacoes) == 1
    assert resultado.processos[0].atualizacoes[0].descricao == "Publicação"
    assert resultado.processos[0].fonte == "datajud"
    assert (
        resultado.processos[0].data_ultima_atualizacao_fonte
        == datetime(2026, 3, 10, 14, 40, tzinfo=timezone.utc)
    )
    assert resultado.processos[0].observacao is not None


def test_consultar_processos_com_base_nao_suportada(monkeypatch):
    monkeypatch.setenv("DATAJUD_API_KEY", "fake-api-key")

    payload = ConsultaInput.model_validate(
        {
            "processos": [
                {
                    "numero_processo": "0000000-00.0000.0.00.0000",
                    "base": "tjsp",
                    "data_base": "2025-01-01",
                }
            ]
        }
    )

    with pytest.raises(ValueError, match="Base ainda não suportada"):
        consultar_processos(payload)