from __future__ import annotations

import csv
from datetime import date, timedelta
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
    processos_monitorados = carregar_processos_monitorados()

    if not processos_monitorados:
        return None

    data_base = date.today() - timedelta(days=dias_busca)

    payload = ConsultaInput.model_validate(
        {
            "processos": [
                {
                    "numero_processo": processo["numero_processo"],
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
        processo.atualizacoes = marcar_movimentacoes_novas(
            numero_processo=processo.numero_processo,
            base=processo.base,
            atualizacoes=processo.atualizacoes,
        )

        salvar_movimentacoes_do_processo(
            numero_processo=processo.numero_processo,
            base=processo.base,
            atualizacoes=processo.atualizacoes,
        )

        for atualizacao in processo.atualizacoes:
            if atualizacao.nova is not True:
                continue

            linhas.append(
                {
                    "processo": processo.numero_processo,
                    "base": processo.base,
                    "fonte": processo.fonte,
                    "data": atualizacao.data_movimentacao.strftime(
                        "%d/%m/%Y %H:%M"
                    ),
                    "descricao": atualizacao.descricao,
                }
            )

    reports_dir = get_reports_dir()
    report_path = reports_dir / f"relatorio_monitorados_{date.today().isoformat()}.csv"

    with report_path.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file:
        fieldnames = [
            "processo",
            "base",
            "fonte",
            "data",
            "descricao",
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
            delimiter=";",
        )

        writer.writeheader()
        writer.writerows(linhas)

    return report_path


def main() -> None:
    bootstrap_local_structure()
    configure_logging()
    load_dotenv(get_env_path())

    initialize_database()

    report_path = gerar_relatorio_monitorados()

    if report_path is None:
        print("Nenhum processo monitorado encontrado.")
        return

    print(f"Relatório gerado em: {report_path}")


if __name__ == "__main__":
    main()