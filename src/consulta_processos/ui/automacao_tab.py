from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path

import streamlit as st

from consulta_processos.email_service import enviar_email
from consulta_processos.jobs.monitorados_report import (
    gerar_relatorio_monitorados,
)
from consulta_processos.logging_config import get_log_path
from consulta_processos.paths import get_reports_dir
from consulta_processos.settings import get_settings
from consulta_processos.utils.dates import (
    format_datetime,
)

logger = logging.getLogger(__name__)


def render_automacao_tab() -> None:
    st.header("⚙️ Automação")

    st.markdown(
        """
        Esta área reúne as funcionalidades automáticas
        e operacionais do JuriScan.

        Use esta aba para:
        - executar monitoramentos
        - testar envio de emails
        - acessar logs e relatórios
        - configurar o agendamento automático
        """
    )

    log_path = get_log_path()
    reports_dir = get_reports_dir()

    render_status_section(
        log_path=log_path,
        reports_dir=reports_dir,
    )

    st.divider()

    render_acoes_manuais_section()

    st.divider()

    render_arquivos_section(
        reports_dir=reports_dir,
        logs_dir=log_path.parent,
    )

    st.divider()

    render_agendamento_section()


def run_email_report() -> None:
    with st.spinner("Executando monitoramento..."):
        try:
            report_path = gerar_relatorio_monitorados()

            if report_path is None:
                st.info("Nenhum processo monitorado cadastrado. Nada foi executado.")
                return

            html = report_path.read_text(encoding="utf-8")

            enviar_email(
                assunto="Relatório de processos monitorados",
                corpo_html=html,
            )

        except Exception as exc:
            st.error("Erro ao executar monitoramento.")
            st.exception(exc)
            return

    st.success("Monitoramento executado com sucesso.")


def get_latest_file_mtime(
    directory: Path,
    pattern: str = "*",
) -> datetime | None:
    if not directory.exists():
        return None

    files = [path for path in directory.rglob(pattern) if path.is_file()]

    if not files:
        return None

    latest_file = max(
        files,
        key=lambda path: path.stat().st_mtime,
    )

    return datetime.fromtimestamp(latest_file.stat().st_mtime)


def render_status_section(
    log_path: Path,
    reports_dir: Path,
) -> None:
    st.subheader("Status")

    settings = get_settings()

    ultima_atividade = (
        datetime.fromtimestamp(log_path.stat().st_mtime) if log_path.exists() else None
    )

    ultimo_relatorio = get_latest_file_mtime(
        reports_dir,
        "*.csv",
    )

    email_status = (
        "Configurado"
        if all(
            [
                settings.email_smtp_host,
                settings.email_username,
                settings.email_password,
                settings.email_from,
                settings.email_to,
            ]
        )
        else "Não configurado"
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Última atividade",
            format_datetime(ultima_atividade) if ultima_atividade else "Nunca",
        )

    with col2:
        st.metric(
            "Último relatório",
            format_datetime(ultimo_relatorio) if ultimo_relatorio else "Nenhum",
        )

    with col3:
        st.metric(
            "Email",
            email_status,
        )


def render_acoes_manuais_section() -> None:
    st.subheader("Ações rápidas")

    st.caption(
        "Use estas ações para testar ou executar rotinas sem depender do agendamento automático."
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "🔄 Rodar monitoramento agora",
            use_container_width=True,
        ):
            run_email_report()

    with col2:
        if st.button(
            "✉️ Testar envio de email",
            use_container_width=True,
        ):
            testar_envio_email()


def testar_envio_email() -> None:
    try:
        enviar_email(
            assunto="Teste JuriScan",
            corpo_html="""
            <h2>Teste de email</h2>
            <p>
                O envio automático de emails do JuriScan
                está funcionando corretamente.
            </p>
            """,
        )

        st.success("Email de teste enviado com sucesso.")

    except Exception as exc:
        logger.exception("Erro ao enviar email de teste")

        st.error(f"Erro ao enviar email de teste: {exc}")


def render_arquivos_section(
    reports_dir: Path,
    logs_dir: Path,
) -> None:
    st.subheader("Arquivos")

    st.caption("Abra rapidamente as pastas utilizadas pelo monitoramento automático.")

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "📂 Abrir relatórios",
            use_container_width=True,
        ):
            reports_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            os.startfile(reports_dir)

    with col2:
        if st.button(
            "📜 Abrir logs",
            use_container_width=True,
        ):
            logs_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            os.startfile(logs_dir)


def render_agendamento_section() -> None:
    st.subheader("Agendamento automático")

    st.caption("Configure o Windows para executar o monitoramento automaticamente todos os dias.")

    st.info(
        """
        Para ativar o monitoramento automático diário, execute:

        `scripts/install_windows_task.bat`

        Para remover o agendamento, execute:

        `scripts/uninstall_windows_task.bat`
        """
    )

    st.warning(
        """
        Antes de ativar o agendamento, teste manualmente:

        1. **Rodar monitoramento agora**
        2. **Testar envio de email**

        Assim você confirma que o ambiente, o banco local e o email
        estão configurados corretamente.
        """
    )
