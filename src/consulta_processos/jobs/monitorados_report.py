from __future__ import annotations

import csv
from datetime import date, timedelta, datetime
from pathlib import Path

from dotenv import load_dotenv

from consulta_processos.bootstrap import bootstrap_local_structure
from consulta_processos.database import initialize_database
from consulta_processos.history_repository import (
    marcar_movimentacoes_novas,
    salvar_movimentacoes_do_processo,
)
from consulta_processos.logging_config import configure_logging
from consulta_processos.models import ConsultaInput
from consulta_processos.monitoring_repository import carregar_processos_monitorados
from consulta_processos.paths import get_app_dir, get_env_path
from consulta_processos.services import consultar_processos


def get_reports_dir() -> Path:
    reports_dir = get_app_dir() / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    return reports_dir


def gerar_relatorio_monitorados(
    dias_busca: int = 7,
) -> Path | None:
    processos_monitorados = (
        carregar_processos_monitorados()
    )

    if not processos_monitorados:
        return None

    cliente_por_processo_base = {
        (
            item["numero_processo"],
            item["base"],
        ): item.get(
            "cliente",
            "Sem cliente",
        )
        for item in processos_monitorados
    }

    data_base = (
        date.today() - timedelta(days=dias_busca)
    )

    payload = ConsultaInput.model_validate(
        {
            "processos": [
                {
                    "numero_processo": processo[
                        "numero_processo"
                    ],
                    "base": processo["base"],
                    "data_base": data_base.isoformat(),
                }
                for processo in processos_monitorados
            ]
        }
    )

    resultado = consultar_processos(payload)

    linhas = []

    for processo in resultado.processos:
        processo.atualizacoes = (
            marcar_movimentacoes_novas(
                numero_processo=processo.numero_processo,
                base=processo.base,
                atualizacoes=processo.atualizacoes,
            )
        )

        salvar_movimentacoes_do_processo(
            numero_processo=processo.numero_processo,
            base=processo.base,
            atualizacoes=processo.atualizacoes,
        )

        cliente = cliente_por_processo_base.get(
            (
                processo.numero_processo,
                processo.base,
            ),
            "Sem cliente",
        )

        for atualizacao in processo.atualizacoes:
            if atualizacao.nova is not True:
                continue

            linhas.append(
                {
                    "cliente": cliente,
                    "processo": processo.numero_processo,
                    "base": processo.base,
                    "fonte": processo.fonte,
                    "data": (
                        atualizacao.data_movimentacao
                        .strftime("%d/%m/%Y %H:%M")
                    ),
                    "descricao": atualizacao.descricao,
                }
            )

    if not linhas:
        return None

    reports_dir = get_reports_dir()

    timestamp = datetime.now().strftime(
        "%Y-%m-%d_%H-%M"
    )

    report_path = (
        reports_dir
        / f"relatorio_completo_{timestamp}.csv"
    )

    fieldnames = [
        "cliente",
        "processo",
        "base",
        "fonte",
        "data",
        "descricao",
    ]

    # =========================
    # RELATÓRIO COMPLETO
    # =========================

    with report_path.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
            delimiter=";",
        )

        writer.writeheader()
        writer.writerows(linhas)

    # =========================
    # RELATÓRIOS POR CLIENTE
    # =========================

    for linha in linhas:
        cliente_dir = (
            reports_dir
            / "clientes"
            / slugify_path(linha["cliente"])
            / slugify_path(linha["processo"])
        )

        cliente_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        cliente_report_path = (
            cliente_dir
            / f"relatorio_{timestamp}.csv"
        )

        arquivo_existe = (
            cliente_report_path.exists()
        )

        with cliente_report_path.open(
            "a",
            newline="",
            encoding="utf-8-sig",
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames,
                delimiter=";",
            )

            if not arquivo_existe:
                writer.writeheader()

            writer.writerow(linha)

    return report_path

def slugify_path(value: str) -> str:
    invalid_chars = '<>:"/\\|?*'

    sanitized = value.strip()

    for char in invalid_chars:
        sanitized = sanitized.replace(char, "_")

    return sanitized or "Sem cliente"

def main() -> None:
    bootstrap_local_structure()
    configure_logging()
    load_dotenv(get_env_path())

    initialize_database()

    report_path = gerar_relatorio_monitorados()

    if report_path is None:
        print(
            "Nenhuma nova movimentação encontrada "
            "nos processos monitorados."
        )
        return

    print(f"Relatório gerado em: {report_path}")


if __name__ == "__main__":
    main()