from datetime import date

import pandas as pd
import streamlit as st

from consulta_processos.models import ConsultaInput
from consulta_processos.services import consultar_processos
from consulta_processos.history_repository import (
    marcar_movimentacoes_novas,
    salvar_movimentacoes_do_processo,
)
from consulta_processos.monitoring_repository import (
    carregar_processos_monitorados,
    remover_processo_monitorado,
)

def render_monitorados_tab(
    enable_local_history: bool,
) -> None:
    st.subheader("Processos monitorados")

    processos_monitorados = (
        carregar_processos_monitorados()
    )

    consultar_monitorados = st.button(
        "Consultar processos monitorados",
        type="primary",
    )

    if not processos_monitorados:
        st.info(
            "Nenhum processo monitorado."
        )

    else:
        for processo in processos_monitorados:
            col1, col2 = st.columns([5, 1])

            with col1:
                st.write(
                    f"📌 {processo['numero_processo']} "
                    f"({processo['base']})"
                )

            with col2:
                remover = st.button(
                    "🗑️ Remover",
                    key=(
                        f"remover_"
                        f"{processo['numero_processo']}"
                    ),
                )

            if remover:
                removido = remover_processo_monitorado(
                    numero_processo=processo[
                        "numero_processo"
                    ],
                    base=processo["base"],
                )

                if removido:
                    st.success(
                        "Processo removido dos monitorados."
                    )
                    st.rerun()

                else:
                    st.error(
                        "Não foi possível remover o processo."
                    )
    if consultar_monitorados:
        if not processos_monitorados:
            st.warning("Nenhum processo monitorado para consultar.")
            st.stop()

        data_base_monitorados = date.today().replace(year=date.today().year - 1)

        payload = ConsultaInput.model_validate(
            {
                "processos": [
                    {
                        "numero_processo": processo["numero_processo"],
                        "base": processo["base"],
                        "data_base": data_base_monitorados.isoformat(),
                    }
                    for processo in processos_monitorados
                ]
            }
        )

        with st.spinner("Consultando processos monitorados..."):
            resultado_monitorados = consultar_processos(payload)

        linhas_monitorados = []

        for processo in resultado_monitorados.processos:
            if enable_local_history:
                processo.atualizacoes = marcar_movimentacoes_novas(
                    numero_processo=processo.numero_processo,
                    base=processo.base,
                    atualizacoes=processo.atualizacoes,
                )

                salvar_movimentacoes_do_processo(
                    numero_processo=processo.numero_processo,
                    base=processo.base,
                    atualizacoes=processo.atualizacoes,
                    data_ultima_atualizacao_fonte=(
                        processo.data_ultima_atualizacao_fonte.isoformat()
                        if processo.data_ultima_atualizacao_fonte
                        else None
                    ),
                )

            for atualizacao in processo.atualizacoes:
                linhas_monitorados.append(
                    {
                        "Processo": processo.numero_processo,
                        "Nova": (
                            "Sim"
                            if atualizacao.nova is True
                            else "Não"
                            if atualizacao.nova is False
                            else "Histórico desativado"
                        ),
                        "Data": atualizacao.data_movimentacao.strftime("%d/%m/%Y %H:%M"),
                        "Descrição": atualizacao.descricao,
                        "Código": atualizacao.codigo,
                        "Órgão julgador": atualizacao.orgao_julgador,
                        "Última atualização DataJud": (
                            processo.data_ultima_atualizacao_fonte.strftime(
                                "%d/%m/%Y %H:%M"
                            )
                            if processo.data_ultima_atualizacao_fonte
                            else None
                        ),
                    }
                )

        if not linhas_monitorados:
            st.info("Nenhuma movimentação encontrada para os processos monitorados.")
        else:
            df_monitorados_resultado = pd.DataFrame(linhas_monitorados)
            total_processos_monitorados = len(processos_monitorados)

            processos_com_novidade = (
                df_monitorados_resultado[
                    df_monitorados_resultado["Nova"] == "Sim"
                ]["Processo"]
                .nunique()
            )

            novas_movimentacoes = (
                df_monitorados_resultado["Nova"]
                .eq("Sim")
                .sum()
            )

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "📌 Processos monitorados",
                total_processos_monitorados,
            )

            col2.metric(
                "🆕 Processos com novidade",
                int(processos_com_novidade),
            )

            col3.metric(
                "📄 Novas movimentações",
                int(novas_movimentacoes),
            )

            st.divider()

            novas_qtd = (
                df_monitorados_resultado["Nova"]
                .eq("Sim")
                .sum()
            )

            st.metric("Novas movimentações encontradas", int(novas_qtd))

            mostrar_apenas_novas = st.checkbox(
                "Mostrar apenas movimentações novas",
                value=False,
            )

            df_monitorados_filtrado = (
                df_monitorados_resultado.copy()
            )

            if mostrar_apenas_novas:
                df_monitorados_filtrado = (
                    df_monitorados_filtrado[
                        df_monitorados_filtrado["Nova"] == "Sim"
                    ]
                )

            st.dataframe(
                df_monitorados_filtrado,
                use_container_width=True,
                hide_index=True,
            )

            csv_monitorados = df_monitorados_filtrado.to_csv(
                index=False
            ).encode("utf-8-sig")

            st.download_button(
                label="Baixar resultado dos monitorados em CSV",
                data=csv_monitorados,
                file_name="resultado_processos_monitorados.csv",
                mime="text/csv",
            )