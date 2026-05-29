import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "src"))

import streamlit as st
from dotenv import load_dotenv

from consulta_processos.bootstrap import (
    bootstrap_local_structure,
)
from consulta_processos.database import initialize_database
from consulta_processos.logging_config import configure_logging
from consulta_processos.paths import get_env_path
from consulta_processos.ui.clientes_tab import render_clientes_tab
from consulta_processos.ui.consulta_tab import render_consulta_tab
from consulta_processos.ui.historico_tab import render_historico_tab
from consulta_processos.ui.monitorados_tab import render_monitorados_tab

bootstrap_local_structure()
configure_logging()
load_dotenv(get_env_path())

ENABLE_LOCAL_HISTORY = os.getenv("ENABLE_LOCAL_HISTORY", "false").lower() == "true"

if ENABLE_LOCAL_HISTORY:
    initialize_database()


def main() -> None:
    st.set_page_config(
        page_title="Consulta de Processos",
        page_icon="⚖️",
        layout="wide",
    )

    st.title("⚖️ Consulta de Processos")

    tab_consulta, tab_historico, tab_monitorados, tab_clientes = st.tabs(
        ["🔎 Consulta", "🗂 Histórico local", "⭐ Monitorados", "👥 Clientes"]
    )

    with tab_consulta:
        render_consulta_tab(
            enable_local_history=ENABLE_LOCAL_HISTORY,
        )

    with tab_historico:
        render_historico_tab(
            enable_local_history=ENABLE_LOCAL_HISTORY,
        )

    with tab_monitorados:
        render_monitorados_tab(
            enable_local_history=ENABLE_LOCAL_HISTORY,
        )

    with tab_clientes:
        render_clientes_tab()


if __name__ == "__main__":
    main()