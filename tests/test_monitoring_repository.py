import json

from consulta_processos.monitoring_repository import (
    adicionar_processo_monitorado,
    carregar_processos_monitorados,
    importar_processos_monitorados,
    limpar_processos_monitorados,
    listar_clientes_monitorados,
    remover_processo_monitorado,
)


def test_adiciona_processo_monitorado(tmp_path, monkeypatch):
    config_dir = tmp_path / "config"
    config_dir.mkdir()

    monitorados_path = config_dir / "processos_monitorados.json"

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
    assert monitorados[0]["numero_processo"] == "0964024-67.2024.8.19.0001"


def test_nao_duplica_monitorado(tmp_path, monkeypatch):
    config_dir = tmp_path / "config"
    config_dir.mkdir()

    monitorados_path = config_dir / "processos_monitorados.json"

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

    monitorados_path = config_dir / "processos_monitorados.json"

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


def test_importar_processos_monitorados_adiciona_varios(
    tmp_path,
    monkeypatch,
):
    monitorados_path = tmp_path / "processos_monitorados.json"
    monitorados_path.write_text("[]", encoding="utf-8")

    monkeypatch.setattr(
        "consulta_processos.monitoring_repository.get_monitored_processes_path",
        lambda: monitorados_path,
    )

    adicionados = importar_processos_monitorados(
        processos=[
            {
                "numero_processo": "0964024-67.2024.8.19.0001",
                "base": "tjrj_datajud",
            },
            {
                "numero_processo": "5000000-00.2025.4.02.0000",
                "base": "trf2_eproc",
            },
        ],
    )

    monitorados = carregar_processos_monitorados()

    assert adicionados == 2
    assert len(monitorados) == 2


def test_importar_processos_monitorados_nao_duplica(
    tmp_path,
    monkeypatch,
):
    monitorados_path = tmp_path / "processos_monitorados.json"
    monitorados_path.write_text(
        """
        [
          {
            "numero_processo": "0964024-67.2024.8.19.0001",
            "base": "tjrj_datajud"
          }
        ]
        """,
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "consulta_processos.monitoring_repository.get_monitored_processes_path",
        lambda: monitorados_path,
    )

    adicionados = importar_processos_monitorados(
        processos=[
            {
                "numero_processo": "0964024-67.2024.8.19.0001",
                "base": "tjrj_datajud",
            },
            {
                "numero_processo": "5000000-00.2025.4.02.0000",
                "base": "trf2_eproc",
            },
        ],
    )

    monitorados = carregar_processos_monitorados()

    assert adicionados == 1
    assert len(monitorados) == 2


def test_importar_processos_monitorados_substitui_lista(
    tmp_path,
    monkeypatch,
):
    monitorados_path = tmp_path / "processos_monitorados.json"
    monitorados_path.write_text(
        """
        [
          {
            "numero_processo": "1111111-11.1111.1.11.1111",
            "base": "tjrj_datajud"
          }
        ]
        """,
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "consulta_processos.monitoring_repository.get_monitored_processes_path",
        lambda: monitorados_path,
    )

    adicionados = importar_processos_monitorados(
        processos=[
            {
                "numero_processo": "0964024-67.2024.8.19.0001",
                "base": "tjrj_datajud",
            }
        ],
        substituir=True,
    )

    monitorados = carregar_processos_monitorados()

    assert adicionados == 1
    assert len(monitorados) == 1
    assert monitorados[0]["numero_processo"] == "0964024-67.2024.8.19.0001"


def test_limpar_processos_monitorados(
    tmp_path,
    monkeypatch,
):
    monitorados_path = tmp_path / "processos_monitorados.json"
    monitorados_path.write_text(
        """
        [
          {
            "numero_processo": "0964024-67.2024.8.19.0001",
            "base": "tjrj_datajud"
          }
        ]
        """,
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "consulta_processos.monitoring_repository.get_monitored_processes_path",
        lambda: monitorados_path,
    )

    limpar_processos_monitorados()

    assert carregar_processos_monitorados() == []


def test_adicionar_processo_monitorado_com_cliente(
    tmp_path,
    monkeypatch,
):
    monitorados_path = tmp_path / "processos_monitorados.json"

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
        cliente="Cliente XPTO",
    )

    monitorados = carregar_processos_monitorados()

    assert monitorados[0]["cliente"] == "Cliente XPTO"


def test_listar_clientes_monitorados(
    tmp_path,
    monkeypatch,
):
    monitorados_path = tmp_path / "processos_monitorados.json"

    monitorados_path.write_text(
        json.dumps(
            [
                {
                    "cliente": "Cliente B",
                    "numero_processo": "1",
                    "base": "tjrj_datajud",
                },
                {
                    "cliente": "Cliente A",
                    "numero_processo": "2",
                    "base": "trf2_eproc",
                },
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "consulta_processos.monitoring_repository.get_monitored_processes_path",
        lambda: monitorados_path,
    )

    clientes = listar_clientes_monitorados()

    assert clientes == [
        "Cliente A",
        "Cliente B",
    ]
