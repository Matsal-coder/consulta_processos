from consulta_processos.database import initialize_database
from consulta_processos.jobs.monitorados_report import (
    gerar_relatorio_monitorados,
    slugify_path,
)
from consulta_processos.monitoring_repository import adicionar_processo_monitorado


def test_gerar_relatorio_sem_monitorados(
    tmp_path,
    monkeypatch,
):
    db_path = tmp_path / "consulta_processos_test.db"

    monkeypatch.setenv(
        "CONSULTA_PROCESSOS_DB_PATH",
        str(db_path),
    )

    initialize_database()

    resultado = gerar_relatorio_monitorados()

    assert resultado is None


def test_slugify_path():
    resultado = slugify_path("Cliente:/Teste?")

    assert resultado == "Cliente__Teste_"


def test_gerar_relatorio_carrega_monitorado_do_sqlite(
    tmp_path,
    monkeypatch,
):
    db_path = tmp_path / "consulta_processos_test.db"

    monkeypatch.setenv(
        "CONSULTA_PROCESSOS_DB_PATH",
        str(db_path),
    )

    initialize_database()

    adicionar_processo_monitorado(
        numero_processo="0964024-67.2024.8.19.0001",
        base="datajud_tjrj",
        cliente="Cliente XPTO",
    )

    def fake_consultar_processos(payload):
        assert len(payload.processos) == 1
        assert payload.processos[0].numero_processo == "0964024-67.2024.8.19.0001"
        assert payload.processos[0].base == "datajud_tjrj"

        raise RuntimeError("stop-after-load")

    monkeypatch.setattr(
        "consulta_processos.jobs.monitorados_report.consultar_processos",
        fake_consultar_processos,
    )

    try:
        gerar_relatorio_monitorados()
    except RuntimeError as exc:
        assert str(exc) == "stop-after-load"
    else:
        raise AssertionError("Expected fake_consultar_processos to stop execution")
