import pandas as pd
import streamlit as st

from consulta_processos.process_repository import (
    atualizar_apelido,
    listar_clientes,
    listar_movimentacoes_processo,
    listar_processos_por_cliente,
    remover_processo,
    salvar_comentario_movimentacao,
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

    processo_dict = next(
        processo
        for processo in processos
        if (
            processo["numero_processo"],
            processo["base"],
        ) == processo_selecionado
    )

    st.subheader("Dados do processo")

    novo_apelido = st.text_input(
        "Apelido",
        value=processo_dict.get("apelido") or "",
    )

    if st.button(
        "Salvar apelido",
    ):
        atualizar_apelido(
            numero_processo=numero_processo,
            base=base,
            apelido=novo_apelido,
        )

        st.success("Apelido atualizado.")
        st.rerun()

    if st.button(
        "🗑 Remover processo salvo",
    ):
        remover_processo(
            numero_processo=numero_processo,
            base=base,
        )

        st.success("Processo removido.")
        st.rerun()

    movimentacoes = listar_movimentacoes_processo(
        numero_processo=numero_processo,
        base=base,
    )

    if movimentacoes:
        df_movimentacoes = pd.DataFrame(movimentacoes)

        st.subheader("Timeline do processo")

        st.dataframe(
            df_movimentacoes,
            use_container_width=True,
            hide_index=True,
        )

        st.divider()

        st.subheader("Comentário da movimentação")

        movimentacao_opcoes = {
            (
                f"{movimentacao['data_movimentacao']} — "
                f"{movimentacao['descricao'][:80]}"
            ): movimentacao
            for movimentacao in movimentacoes
        }

        movimentacao_label = st.selectbox(
            "Selecione a movimentação",
            options=list(movimentacao_opcoes.keys()),
        )

        movimentacao_selecionada = movimentacao_opcoes[
            movimentacao_label
        ]

        comentario = st.text_area(
            "Comentário",
            value=movimentacao_selecionada.get("comentario") or "",
            key=f"comentario_{movimentacao_selecionada['id']}",
        )

        if st.button(
            "Salvar comentário",
            key=f"salvar_comentario_{movimentacao_selecionada['id']}",
        ):
            salvar_comentario_movimentacao(
                movimentacao_id=movimentacao_selecionada["id"],
                comentario=comentario,
            )

            st.success("Comentário salvo.")
            st.rerun()

    else:
        st.info("Nenhuma movimentação encontrada.")