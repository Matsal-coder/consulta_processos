from consulta_processos.database import get_connection


def carregar_processos_monitorados() -> list[dict]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                numero_processo,
                base,
                cliente
            FROM processos_cadastrados
            WHERE monitorado = 1
            ORDER BY created_at DESC;
            """
        ).fetchall()

    return [dict(row) for row in rows]


def salvar_processos_monitorados(
    processos: list[dict],
) -> None:
    limpar_processos_monitorados()

    for processo in processos:
        adicionar_processo_monitorado(
            numero_processo=processo["numero_processo"],
            base=processo["base"],
            cliente=processo.get("cliente", "Sem cliente"),
        )


def adicionar_processo_monitorado(
    numero_processo: str,
    base: str,
    cliente: str = "Sem cliente",
) -> bool:
    cliente = cliente.strip() or "Sem cliente"

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT monitorado
            FROM processos_cadastrados
            WHERE numero_processo = ?
              AND base = ?;
            """,
            (
                numero_processo,
                base,
            ),
        ).fetchone()

        if row is not None and row["monitorado"] == 1:
            return False

        if row is None:
            connection.execute(
                """
                INSERT INTO processos_cadastrados (
                    numero_processo,
                    base,
                    cliente,
                    monitorado
                )
                VALUES (?, ?, ?, 1);
                """,
                (
                    numero_processo,
                    base,
                    cliente,
                ),
            )
        else:
            connection.execute(
                """
                UPDATE processos_cadastrados
                SET monitorado = 1
                WHERE numero_processo = ?
                  AND base = ?;
                """,
                (
                    numero_processo,
                    base,
                ),
            )

    return True


def remover_processo_monitorado(
    numero_processo: str,
    base: str,
) -> bool:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE processos_cadastrados
            SET monitorado = 0
            WHERE numero_processo = ?
              AND base = ?
              AND monitorado = 1;
            """,
            (
                numero_processo,
                base,
            ),
        )

    return cursor.rowcount == 1


def limpar_processos_monitorados() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE processos_cadastrados
            SET monitorado = 0
            WHERE monitorado = 1;
            """
        )


def importar_processos_monitorados(
    processos: list[dict],
    substituir: bool = False,
) -> int:
    if substituir:
        limpar_processos_monitorados()

    adicionados = 0

    for processo in processos:
        numero_processo = processo["numero_processo"]
        base = processo["base"]
        cliente = processo.get("cliente", "Sem cliente").strip() or "Sem cliente"

        foi_adicionado = adicionar_processo_monitorado(
            numero_processo=numero_processo,
            base=base,
            cliente=cliente,
        )

        if foi_adicionado:
            adicionados += 1

    return adicionados


def listar_clientes_monitorados() -> list[str]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT DISTINCT cliente
            FROM processos_cadastrados
            WHERE monitorado = 1
            ORDER BY cliente;
            """
        ).fetchall()

    return [row["cliente"] for row in rows]
