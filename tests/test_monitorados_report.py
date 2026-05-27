from consulta_processos.jobs.monitorados_report import (
    gerar_relatorio_monitorados,
    slugify_path,
)


def test_gerar_relatorio_sem_monitorados(
    tmp_path,
    monkeypatch,
):
    monitorados_path = (
        tmp_path / "processos_monitorados.json"
    )

    monitorados_path.write_text(
        "[]",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "consulta_processos.monitoring_repository.get_monitored_processes_path",
        lambda: monitorados_path,
    )

    resultado = gerar_relatorio_monitorados()

    assert resultado is None


def test_slugify_path():
    resultado = slugify_path(
        'Cliente:/Teste?'
    )

    assert resultado == "Cliente__Teste_"