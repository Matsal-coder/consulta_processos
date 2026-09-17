from datetime import datetime, timezone

from consulta_processos.database import initialize_database
from consulta_processos.history_repository import (
    listar_movimentacoes_salvas,
    marcar_movimentacoes_novas,
    salvar_movimentacoes_do_processo,
)
from consulta_processos.models import AtualizacaoProcesso


def test_salvar_movimentacao_no_historico(tmp_path, monkeypatch):
    db_path = tmp_path / "consulta_processos_test.db"

    monkeypatch.setenv(
        "CONSULTA_PROCESSOS_DB_PATH",
        str(db_path),
    )

    initialize_database()

    atualizacao = AtualizacaoProcesso(
        descricao="Publicação",
        data_movimentacao=datetime(
            2025,
            1,
            23,
            tzinfo=timezone.utc,
        ),
    )

    novas = salvar_movimentacoes_do_processo(
        numero_processo="0964024-67.2024.8.19.0001",
        base="tjrj_datajud",
        atualizacoes=[atualizacao],
    )

    assert novas == 1

    salvas = listar_movimentacoes_salvas()

    assert len(salvas) == 1
    assert salvas[0]["numero_processo"] == "0964024-67.2024.8.19.0001"
    assert salvas[0]["base"] == "tjrj_datajud"
    assert salvas[0]["descricao"] == "Publicação"


def test_nao_duplica_movimentacao_no_historico(tmp_path, monkeypatch):
    db_path = tmp_path / "consulta_processos_test.db"

    monkeypatch.setenv(
        "CONSULTA_PROCESSOS_DB_PATH",
        str(db_path),
    )

    initialize_database()

    atualizacao = AtualizacaoProcesso(
        descricao="Publicação",
        data_movimentacao=datetime(
            2025,
            1,
            23,
            tzinfo=timezone.utc,
        ),
    )

    primeira = salvar_movimentacoes_do_processo(
        numero_processo="0964024-67.2024.8.19.0001",
        base="tjrj_datajud",
        atualizacoes=[atualizacao],
    )

    segunda = salvar_movimentacoes_do_processo(
        numero_processo="0964024-67.2024.8.19.0001",
        base="tjrj_datajud",
        atualizacoes=[atualizacao],
    )

    assert primeira == 1
    assert segunda == 0
    assert len(listar_movimentacoes_salvas()) == 1


def test_marcar_movimentacoes_novas(tmp_path, monkeypatch):
    db_path = tmp_path / "consulta_processos_test.db"

    monkeypatch.setenv(
        "CONSULTA_PROCESSOS_DB_PATH",
        str(db_path),
    )

    initialize_database()

    atualizacao_antiga = AtualizacaoProcesso(
        descricao="Publicação",
        data_movimentacao=datetime(
            2025,
            1,
            23,
            tzinfo=timezone.utc,
        ),
    )

    salvar_movimentacoes_do_processo(
        numero_processo="0964024-67.2024.8.19.0001",
        base="tjrj_datajud",
        atualizacoes=[atualizacao_antiga],
    )

    atualizacoes_marcadas = marcar_movimentacoes_novas(
        numero_processo="0964024-67.2024.8.19.0001",
        base="tjrj_datajud",
        atualizacoes=[
            atualizacao_antiga,
            AtualizacaoProcesso(
                descricao="Conclusão",
                data_movimentacao=datetime(
                    2025,
                    2,
                    1,
                    tzinfo=timezone.utc,
                ),
            ),
        ],
    )

    assert atualizacoes_marcadas[0].nova is False
    assert atualizacoes_marcadas[1].nova is True
