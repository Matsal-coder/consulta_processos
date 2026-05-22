import pandas as pd
import streamlit as st

from consulta_processos.history_repository import (
    listar_movimentacoes_salvas
)


def render_historico_tab(
    enable_local_history: bool,
) -> None:
    st.subheader("Histórico local de movimentações")

    if not enable_local_history:
        st.warning(
            "Histórico local desabilitado. "
            "Ative ENABLE_LOCAL_HISTORY=true no .env."
        )

    else:
        movimentacoes_salvas = listar_movimentacoes_salvas()

        if not movimentacoes_salvas:
            st.info("Nenhuma movimentação salva ainda.")

        else:
            df_historico = pd.DataFrame(
                movimentacoes_salvas
            )

            df_historico["data_movimentacao"] = pd.to_datetime(
                df_historico["data_movimentacao"],
                format="mixed",
                errors="coerce",
                utc=True,
            )

            df_historico["created_at"] = pd.to_datetime(
                df_historico["created_at"]
            )

            filtro_processo = st.text_input(
                "Filtrar por processo",
                key="historico_filtro_processo",
            )

            if filtro_processo:
                df_historico = df_historico[
                    df_historico["numero_processo"]
                    .str.contains(
                        filtro_processo,
                        case=False,
                        na=False,
                    )
                ]

            st.dataframe(
                df_historico,
                use_container_width=True,
                hide_index=True,
            )

            csv = df_historico.to_csv(
                index=False
            ).encode("utf-8-sig")

            st.download_button(
                label="Baixar histórico em CSV",
                data=csv,
                file_name="historico_movimentacoes.csv",
                mime="text/csv",
            )

