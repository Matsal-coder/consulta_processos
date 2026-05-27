from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

from dotenv import load_dotenv

from consulta_processos.bootstrap import (
    bootstrap_local_structure,
)
from consulta_processos.database import (
    initialize_database,
)
from consulta_processos.email_service import (
    enviar_email,
    is_email_enabled,
)
from consulta_processos.jobs.monitorados_report import (
    gerar_relatorio_monitorados,
)
from consulta_processos.logging_config import (
    configure_logging,
)
from consulta_processos.paths import (
    get_env_path,
)


def carregar_linhas_csv(
    report_path: Path,
) -> list[dict]:
    with report_path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(
            file,
            delimiter=";",
        )

        return list(reader)


def montar_tabela_html(
    linhas: list[dict],
) -> str:
    resumo_por_cliente = defaultdict(
        lambda: defaultdict(int)
    )

    for linha in linhas:
        resumo_por_cliente[
            linha["cliente"]
        ][linha["processo"]] += 1

    clientes_afetados = len(
        resumo_por_cliente
    )

    processos_afetados = sum(
        len(processos)
        for processos in resumo_por_cliente.values()
    )

    resumo_html = ""

    for cliente, processos in (
        resumo_por_cliente.items()
    ):
        resumo_html += (
            f"<h3>{cliente}</h3><ul>"
        )

        for (
            processo,
            quantidade,
        ) in processos.items():
            resumo_html += (
                f"<li>"
                f"{processo} — "
                f"{quantidade} movimentação(ões)"
                f"</li>"
            )

        resumo_html += "</ul>"

    linhas_html = ""

    for linha in linhas:
        linhas_html += f"""
        <tr>
            <td>{linha["cliente"]}</td>
            <td>{linha["processo"]}</td>
            <td>{linha["base"]}</td>
            <td>{linha["data"]}</td>
            <td>{linha["descricao"]}</td>
        </tr>
        """

    return f"""
    <html>
        <body>
            <h2>
                JuriScan - Novas movimentações
            </h2>

            <p>
                Foram encontradas
                <strong>{len(linhas)}</strong>
                nova(s) movimentação(ões).
            </p>

            <p>
                Clientes afetados:
                <strong>
                    {clientes_afetados}
                </strong>
                <br>

                Processos afetados:
                <strong>
                    {processos_afetados}
                </strong>
            </p>

            <h3>Resumo por cliente</h3>

            {resumo_html}

            <hr>

            <h3>
                Detalhamento completo
            </h3>

            <table
                border="1"
                cellpadding="6"
                cellspacing="0"
            >
                <thead>
                    <tr>
                        <th>Cliente</th>
                        <th>Processo</th>
                        <th>Base</th>
                        <th>Data</th>
                        <th>Descrição</th>
                    </tr>
                </thead>

                <tbody>
                    {linhas_html}
                </tbody>
            </table>
        </body>
    </html>
    """


def main() -> None:
    bootstrap_local_structure()

    configure_logging()

    load_dotenv(get_env_path())

    initialize_database()

    if not is_email_enabled():
        print(
            "Envio de email desabilitado."
        )
        return

    report_path = (
        gerar_relatorio_monitorados()
    )

    if report_path is None:
        print(
            "Nenhuma nova movimentação "
            "encontrada. "
            "Email não enviado."
        )
        return

    linhas = carregar_linhas_csv(
        report_path
    )

    corpo_html = montar_tabela_html(
        linhas
    )

    enviar_email(
        assunto=(
            f"[JuriScan] "
            f"{len(linhas)} "
            f"nova(s) movimentação(ões)"
        ),
        corpo_html=corpo_html,
    )

    print("Email enviado com sucesso.")


if __name__ == "__main__":
    main()