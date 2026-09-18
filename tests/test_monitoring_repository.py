from consulta_processos.database import initialize_database
from consulta_processos.monitoring_repository import (
    adicionar_processo_monitorado,
    carregar_processos_monitorados,
    importar_processos_monitorados,
    limpar_processos_monitorados,
    listar_clientes_monitorados,
    remover_processo_monitorado,
    salvar_processos_monitorados,
)
from consulta_processos.process_repository import (
    listar_processos_por_cliente,
    salvar_processo,
)


def test_adiciona_processo_monitorado(tmp_path, monkeypatch):
    db_path = tmp_path / "consulta_processos_test.db"

    monkeypatch.setenv(
        "CONSULTA_PROCESSOS_DB_PATH",
        str(db_path),
    )

    initialize_database()

    adicionar_processo_monitorado(
        numero_processo="0964024-67.2024.8.19.0001",
        base="tjrj_datajud",
    )

    monitorados = carregar_processos_monitorados()

    assert len(monitorados) == 1
    assert monitorados[0]["numero_processo"] == "0964024-67.2024.8.19.0001"


def test_nao_duplica_monitorado(tmp_path, monkeypatch):
    db_path = tmp_path / "consulta_processos_test.db"

    monkeypatch.setenv(
        "CONSULTA_PROCESSOS_DB_PATH",
        str(db_path),
    )

    initialize_database()

    primeiro = adicionar_processo_monitorado(
        numero_processo="0964024-67.2024.8.19.0001",
        base="tjrj_datajud",
    )

    segundo = adicionar_processo_monitorado(
        numero_processo="0964024-67.2024.8.19.0001",
        base="tjrj_datajud",
    )

    monitorados = carregar_processos_monitorados()

    assert primeiro is True
    assert segundo is False
    assert len(monitorados) == 1


def test_remove_processo_monitorado(tmp_path, monkeypatch):
    db_path = tmp_path / "consulta_processos_test.db"

    monkeypatch.setenv(
        "CONSULTA_PROCESSOS_DB_PATH",
        str(db_path),
    )

    initialize_database()

    adicionar_processo_monitorado(
        numero_processo="0964024-67.2024.8.19.0001",
        base="tjrj_datajud",
    )

    removido = remover_processo_monitorado(
        numero_processo="0964024-67.2024.8.19.0001",
        base="tjrj_datajud",
    )

    monitorados = carregar_processos_monitorados()

    assert removido is True
    assert monitorados == []


def test_importar_processos_monitorados_adiciona_varios(
    tmp_path,
    monkeypatch,
):
    db_path = tmp_path / "consulta_processos_test.db"

    monkeypatch.setenv(
        "CONSULTA_PROCESSOS_DB_PATH",
        str(db_path),
    )

    initialize_database()

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
    db_path = tmp_path / "consulta_processos_test.db"

    monkeypatch.setenv(
        "CONSULTA_PROCESSOS_DB_PATH",
        str(db_path),
    )

    initialize_database()

    adicionar_processo_monitorado(
        numero_processo="0964024-67.2024.8.19.0001",
        base="tjrj_datajud",
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
    db_path = tmp_path / "consulta_processos_test.db"

    monkeypatch.setenv(
        "CONSULTA_PROCESSOS_DB_PATH",
        str(db_path),
    )

    initialize_database()

    adicionar_processo_monitorado(
        numero_processo="1111111-11.1111.1.11.1111",
        base="tjrj_datajud",
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
    db_path = tmp_path / "consulta_processos_test.db"

    monkeypatch.setenv(
        "CONSULTA_PROCESSOS_DB_PATH",
        str(db_path),
    )

    initialize_database()

    adicionar_processo_monitorado(
        numero_processo="0964024-67.2024.8.19.0001",
        base="tjrj_datajud",
    )

    adicionar_processo_monitorado(
        numero_processo="5000000-00.2025.4.02.0000",
        base="trf2_eproc",
    )

    limpar_processos_monitorados()

    assert carregar_processos_monitorados() == []


def test_adicionar_processo_monitorado_com_cliente(
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
        base="tjrj_datajud",
        cliente="Cliente XPTO",
    )

    monitorados = carregar_processos_monitorados()

    assert monitorados[0]["cliente"] == "Cliente XPTO"


def test_listar_clientes_monitorados(
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
        numero_processo="1",
        base="tjrj_datajud",
        cliente="Cliente B",
    )

    adicionar_processo_monitorado(
        numero_processo="2",
        base="trf2_eproc",
        cliente="Cliente A",
    )

    clientes = listar_clientes_monitorados()

    assert clientes == [
        "Cliente A",
        "Cliente B",
    ]


def test_monitorado_persiste_apos_nova_conexao(
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

    monitorados_primeira_leitura = carregar_processos_monitorados()

    assert len(monitorados_primeira_leitura) == 1

    monitorados_segunda_leitura = carregar_processos_monitorados()

    assert len(monitorados_segunda_leitura) == 1
    assert monitorados_segunda_leitura[0]["numero_processo"] == "0964024-67.2024.8.19.0001"
    assert monitorados_segunda_leitura[0]["base"] == "datajud_tjrj"
    assert monitorados_segunda_leitura[0]["cliente"] == "Cliente XPTO"


def test_cliente_vazio_vira_sem_cliente(
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
        cliente="",
    )

    monitorados = carregar_processos_monitorados()

    assert monitorados[0]["cliente"] == "Sem cliente"


def test_remover_monitoramento_preserva_processo_cadastrado(
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

    remover_processo_monitorado(
        numero_processo="0964024-67.2024.8.19.0001",
        base="datajud_tjrj",
    )

    assert carregar_processos_monitorados() == []

    processos = listar_processos_por_cliente("Cliente XPTO")

    assert len(processos) == 1
    assert processos[0]["numero_processo"] == "0964024-67.2024.8.19.0001"


def test_monitorar_processo_ja_cadastrado(
    tmp_path,
    monkeypatch,
):
    db_path = tmp_path / "consulta_processos_test.db"

    monkeypatch.setenv(
        "CONSULTA_PROCESSOS_DB_PATH",
        str(db_path),
    )

    initialize_database()

    salvar_processo(
        numero_processo="0964024-67.2024.8.19.0001",
        base="datajud_tjrj",
        cliente="Cliente XPTO",
        apelido="Processo principal",
    )

    adicionado = adicionar_processo_monitorado(
        numero_processo="0964024-67.2024.8.19.0001",
        base="datajud_tjrj",
        cliente="Cliente XPTO",
    )

    monitorados = carregar_processos_monitorados()
    processos = listar_processos_por_cliente("Cliente XPTO")

    assert adicionado is True
    assert len(monitorados) == 1
    assert len(processos) == 1
    assert processos[0]["apelido"] == "Processo principal"


def test_salvar_processos_monitorados_substitui_lista(
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
        numero_processo="111",
        base="datajud_tjrj",
        cliente="Cliente Antigo",
    )

    salvar_processos_monitorados(
        [
            {
                "numero_processo": "222",
                "base": "eproc_trf2",
                "cliente": "Cliente Novo",
            }
        ]
    )

    monitorados = carregar_processos_monitorados()

    assert len(monitorados) == 1
    assert monitorados[0]["numero_processo"] == "222"
    assert monitorados[0]["cliente"] == "Cliente Novo"
