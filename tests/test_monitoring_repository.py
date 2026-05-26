import json

from consulta_processos.monitoring_repository import (
    adicionar_processo_monitorado,
    carregar_processos_monitorados,
    remover_processo_monitorado,
)


def test_adiciona_processo_monitorado(tmp_path, monkeypatch):
    config_dir = tmp_path / "config"
    config_dir.mkdir()

    monitorados_path = (
        config_dir / "processos_monitorados.json"
    )

    monitorados_path.write_text(
        "[]",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "consulta_processos.monitoring_repository.get_monitored_processes_path",
        lambda: monitorados_path,
    )

    adicionar_processo_monitorado(
        numero_processo="0964024-67.2024.8.19.0001",
        base="tjrj_datajud",
    )

    monitorados = carregar_processos_monitorados()

    assert len(monitorados) == 1
    assert (
        monitorados[0]["numero_processo"]
        == "0964024-67.2024.8.19.0001"
    )


def test_nao_duplica_monitorado(tmp_path, monkeypatch):
    config_dir = tmp_path / "config"
    config_dir.mkdir()

    monitorados_path = (
        config_dir / "processos_monitorados.json"
    )

    monitorados_path.write_text(
        "[]",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "consulta_processos.monitoring_repository.get_monitored_processes_path",
        lambda: monitorados_path,
    )

    adicionar_processo_monitorado(
        numero_processo="0964024-67.2024.8.19.0001",
        base="tjrj_datajud",
    )

    adicionar_processo_monitorado(
        numero_processo="0964024-67.2024.8.19.0001",
        base="tjrj_datajud",
    )

    monitorados = carregar_processos_monitorados()

    assert len(monitorados) == 1


def test_remove_processo_monitorado(tmp_path, monkeypatch):
    config_dir = tmp_path / "config"
    config_dir.mkdir()

    monitorados_path = (
        config_dir / "processos_monitorados.json"
    )

    monitorados_path.write_text(
        json.dumps(
            [
                {
                    "numero_processo": "0964024-67.2024.8.19.0001",
                    "base": "tjrj_datajud",
                }
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "consulta_processos.monitoring_repository.get_monitored_processes_path",
        lambda: monitorados_path,
    )

    remover_processo_monitorado(
        numero_processo="0964024-67.2024.8.19.0001",
        base="tjrj_datajud",
    )

    monitorados = carregar_processos_monitorados()

    assert monitorados == []