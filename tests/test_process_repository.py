from consulta_processos.database import initialize_database
from consulta_processos.process_repository import (
    atualizar_apelido,
    listar_clientes,
    listar_processos_por_cliente,
    remover_processo,
    salvar_comentario_movimentacao,
    salvar_processo,
)


def test_salvar_processo_cadastrado(tmp_path, monkeypatch):
    db_path = tmp_path / "consulta_processos_test.db"

    monkeypatch.setenv(
        "CONSULTA_PROCESSOS_DB_PATH",
        str(db_path),
    )

    initialize_database()

    criado = salvar_processo(
        numero_processo="0964024-67.2024.8.19.0001",
        base="tjrj_datajud",
        cliente="Cliente XPTO",
        apelido="Ação principal",
    )

    assert criado is True

    processos = listar_processos_por_cliente(
        "Cliente XPTO",
    )

    assert len(processos) == 1
    assert processos[0]["numero_processo"] == "0964024-67.2024.8.19.0001"
    assert processos[0]["base"] == "tjrj_datajud"
    assert processos[0]["apelido"] == "Ação principal"


def test_nao_duplica_processo_cadastrado(tmp_path, monkeypatch):
    db_path = tmp_path / "consulta_processos_test.db"

    monkeypatch.setenv(
        "CONSULTA_PROCESSOS_DB_PATH",
        str(db_path),
    )

    initialize_database()

    primeiro = salvar_processo(
        numero_processo="0964024-67.2024.8.19.0001",
        base="tjrj_datajud",
        cliente="Cliente XPTO",
    )

    segundo = salvar_processo(
        numero_processo="0964024-67.2024.8.19.0001",
        base="tjrj_datajud",
        cliente="Cliente XPTO",
    )

    assert primeiro is True
    assert segundo is False


def test_listar_clientes(tmp_path, monkeypatch):
    db_path = tmp_path / "consulta_processos_test.db"

    monkeypatch.setenv(
        "CONSULTA_PROCESSOS_DB_PATH",
        str(db_path),
    )

    initialize_database()

    salvar_processo(
        numero_processo="1",
        base="tjrj_datajud",
        cliente="Cliente B",
    )

    salvar_processo(
        numero_processo="2",
        base="tjrj_datajud",
        cliente="Cliente A",
    )

    clientes = listar_clientes()

    assert clientes == [
        "Cliente A",
        "Cliente B",
    ]


def test_atualizar_apelido(tmp_path, monkeypatch):
    db_path = tmp_path / "consulta_processos_test.db"

    monkeypatch.setenv(
        "CONSULTA_PROCESSOS_DB_PATH",
        str(db_path),
    )

    initialize_database()

    salvar_processo(
        numero_processo="0964024-67.2024.8.19.0001",
        base="tjrj_datajud",
        cliente="Cliente XPTO",
        apelido="Antigo",
    )

    atualizar_apelido(
        numero_processo="0964024-67.2024.8.19.0001",
        base="tjrj_datajud",
        apelido="Novo apelido",
    )

    processos = listar_processos_por_cliente(
        "Cliente XPTO",
    )

    assert processos[0]["apelido"] == "Novo apelido"


def test_salvar_comentario_movimentacao(tmp_path, monkeypatch):
    db_path = tmp_path / "consulta_processos_test.db"

    monkeypatch.setenv(
        "CONSULTA_PROCESSOS_DB_PATH",
        str(db_path),
    )

    initialize_database()

    with initialize_database.__globals__["get_connection"]() as connection:
        cursor = connection.execute(
            """
            INSERT INTO movimentacoes_consultadas (
                numero_processo,
                base,
                descricao,
                data_movimentacao
            )
            VALUES (?, ?, ?, ?);
            """,
            (
                "0964024-67.2024.8.19.0001",
                "tjrj_datajud",
                "Publicação",
                "2025-01-23T00:00:00+00:00",
            ),
        )

        movimentacao_id = cursor.lastrowid

    salvar_comentario_movimentacao(
        movimentacao_id=movimentacao_id,
        comentario="Comentário de teste",
    )

    with initialize_database.__globals__["get_connection"]() as connection:
        row = connection.execute(
            """
            SELECT comentario
            FROM movimentacoes_consultadas
            WHERE id = ?;
            """,
            (movimentacao_id,),
        ).fetchone()

    assert row["comentario"] == "Comentário de teste"


def test_remover_processo(tmp_path, monkeypatch):
    db_path = tmp_path / "consulta_processos_test.db"

    monkeypatch.setenv(
        "CONSULTA_PROCESSOS_DB_PATH",
        str(db_path),
    )

    initialize_database()

    salvar_processo(
        numero_processo="123",
        base="tjrj_datajud",
        cliente="Cliente XPTO",
    )

    remover_processo(
        numero_processo="123",
        base="tjrj_datajud",
    )

    processos = listar_processos_por_cliente(
        "Cliente XPTO",
    )

    assert processos == []
