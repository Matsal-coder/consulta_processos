from __future__ import annotations

import subprocess
from pathlib import Path

import streamlit as st

from consulta_processos.logging_config import get_log_path
from consulta_processos.paths import get_app_dir


def render_automacao_tab() -> None:
    st.header("Automação")

    st.markdown(
        """
        Esta área reúne as rotinas automáticas do JuriScan.

        Use esta aba para rodar o monitoramento manualmente,
        localizar relatórios e verificar logs da aplicação.
        """
    )

    app_dir = get_app_dir()
    log_path = get_log_path()
    reports_dir = app_dir / "reports"

    st.subheader("Arquivos locais")

    st.write(f"**Pasta da aplicação:** `{app_dir}`")
    st.write(f"**Logs:** `{log_path}`")
    st.write(f"**Relatórios:** `{reports_dir}`")

    st.subheader("Monitoramento")

    if st.button("Rodar monitoramento agora"):
        run_email_report()

    st.info(
        """
        Para ativar o monitoramento automático diário,
        execute o arquivo:

        `scripts/install_windows_task.bat`

        Para remover:

        `scripts/uninstall_windows_task.bat`
        """
    )


def run_email_report() -> None:
    project_root = Path.cwd()
    script_path = (
        project_root
        / "scripts"
        / "run_email_report.bat"
    )

    if not script_path.exists():
        st.error(
            "Script de monitoramento não encontrado: "
            f"{script_path}"
        )
        return

    with st.spinner("Executando monitoramento..."):
        result = subprocess.run(
            [str(script_path)],
            cwd=project_root,
            capture_output=True,
            text=True,
            shell=True,
            check=False,
        )

    if result.returncode == 0:
        st.success("Monitoramento executado com sucesso.")
    else:
        st.error("Erro ao executar monitoramento.")
        st.code(result.stderr or result.stdout)