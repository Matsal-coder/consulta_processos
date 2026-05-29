import pandas as pd
import streamlit as st

from consulta_processos.process_repository import (
    listar_clientes,
    listar_movimentacoes_processo,
    listar_processos_por_cliente,
)


def render_clientes_tab() -> None:
    st.subheader("Clientes")

    clientes = listar_clientes()

    if not clientes:
        st.info("Nenhum cliente cadastrado ainda.")
        return

    cliente = st.selectbox(
        "Selecione um cliente",
        options=clientes,
    )

    processos = listar_processos_por_cliente(cliente)

    if not processos:
        st.info("Nenhum processo cadastrado para este cliente.")
        return

    df_processos = pd.DataFrame(processos)
    df_processos["created_at"] = (
        pd.to_datetime(
            df_processos["created_at"],
            utc=True,
        )
        .dt.tz_convert("America/Sao_Paulo")
        .dt.strftime("%d/%m/%Y %H:%M")
    )
    processos_options = [
        (
            processo["numero_processo"],
            processo["base"],
        )
        for processo in processos
    ]

    st.dataframe(
        df_processos,
        use_container_width=True,
        hide_index=True,
    )
    processo_selecionado = st.selectbox(
        "Selecione um processo",
        options=processos_options,
        format_func=lambda x: (
            f"{x[0]} ({x[1]})"
        ),
    )

    numero_processo, base = processo_selecionado

    movimentacoes = listar_movimentacoes_processo(
        numero_processo=numero_processo,
        base=base,
    )

    if movimentacoes:
        df_movimentacoes = pd.DataFrame(
            movimentacoes
        )

        st.subheader(
            "Timeline do processo"
        )

        st.dataframe(
            df_movimentacoes,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info(
            "Nenhuma movimentação encontrada."
        )