import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "src"))

import streamlit as st

from consulta_processos.bootstrap import (
    bootstrap_local_structure,
)
from consulta_processos.database import initialize_database
from consulta_processos.logging_config import configure_logging
from consulta_processos.settings import get_settings
from consulta_processos.ui.automacao_tab import render_automacao_tab
from consulta_processos.ui.clientes_tab import render_clientes_tab
from consulta_processos.ui.consulta_tab import render_consulta_tab
from consulta_processos.ui.historico_tab import render_historico_tab
from consulta_processos.ui.monitorados_tab import render_monitorados_tab

configure_logging()
settings = get_settings()

ENABLE_LOCAL_HISTORY = settings.enable_local_history

if ENABLE_LOCAL_HISTORY:
    initialize_database()


def main() -> None:
    bootstrap_local_structure()
    st.set_page_config(
        page_title="Consulta de Processos",
        page_icon="⚖️",
        layout="wide",
    )

    st.title("⚖️ Consulta de Processos")

    tab_consulta, tab_historico, tab_monitorados, tab_clientes, tab_automacao = st.tabs(
        ["🔎 Consulta", "🗂 Histórico local", "⭐ Monitorados", "👥 Clientes", "⚙️ Automação"]
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
    
    with tab_automacao:
        render_automacao_tab()


if __name__ == "__main__":
    main()