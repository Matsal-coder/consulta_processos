from datetime import date, timedelta
import pandas as pd
import streamlit as st

from consulta_processos.models import ConsultaInput
from consulta_processos.ui.cached_services import consultar_processos_cached
from consulta_processos.history_repository import (
    marcar_movimentacoes_novas,
    salvar_movimentacoes_do_processo,
)
from consulta_processos.monitoring_repository import (
    carregar_processos_monitorados,
    remover_processo_monitorado,
    importar_processos_monitorados,
    limpar_processos_monitorados,
)

def parse_monitorados_texto(
    texto: str,
) -> list[dict]:
    processos = []

    for linha in texto.splitlines():
        linha = linha.strip()

        if not linha:
            continue

        partes = [
            parte.strip()
            for parte in linha.split(";")
        ]

        if len(partes) != 2:
            raise ValueError(
                "Cada linha deve seguir o formato: numero_processo;base"
            )

        numero_processo, base = partes

        processos.append(
            {
                "numero_processo": numero_processo,
                "base": base,
            }
        )

    return processos

def render_monitorados_tab(
    enable_local_history: bool,
) -> None:
    
    st.subheader("Processos monitorados")

    with st.expander("⚙️ Gestão em massa de monitorados"):
        st.caption(
            "Formato esperado: numero_processo;base"
        )

        texto_importacao = st.text_area(
            "Importar monitorados",
            placeholder=(
                "0964024-67.2024.8.19.0001;tjrj_datajud\n"
                "5000000-00.2025.4.02.0000;trf2_eproc"
            ),
            height=120,
        )

        substituir = st.checkbox(
            "Substituir lista atual",
            value=False,
        )

        col_importar, col_limpar = st.columns(2)

        with col_importar:
            if st.button("📥 Importar lista"):
                try:
                    processos_importados = parse_monitorados_texto(
                        texto_importacao
                    )

                    adicionados = importar_processos_monitorados(
                        processos=processos_importados,
                        substituir=substituir,
                    )

                    st.success(
                        f"{adicionados} processo(s) importado(s)."
                    )
                    st.rerun()

                except ValueError as exc:
                    st.error(str(exc))

        with col_limpar:
            if st.button("🧹 Limpar todos"):
                limpar_processos_monitorados()
                st.success("Lista de monitorados limpa.")
                st.rerun()

    processos_monitorados = (
        carregar_processos_monitorados()
    )

    if processos_monitorados:
        df_export_monitorados = pd.DataFrame(
            processos_monitorados
        )

        csv_monitorados_lista = (
            df_export_monitorados
            .to_csv(index=False, sep=";")
            .encode("utf-8-sig")
        )

        st.download_button(
            label="⬇️ Baixar lista de monitorados",
            data=csv_monitorados_lista,
            file_name="processos_monitorados.csv",
            mime="text/csv",
        )

    consultar_monitorados = st.button(
        "🔄 Atualizar monitorados",
        type="primary",
    )

    st.caption(
        "Consulta automática dos processos monitorados considerando os últimos 7 dias."
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

        data_base_monitorados = date.today() - timedelta(days=7)

        payload_dict = {
            "processos": [
                {
                    "numero_processo": processo["numero_processo"],
                    "base": processo["base"],
                    "data_base": data_base_monitorados.isoformat(),
                }
                for processo in processos_monitorados
            ]
        }

        ConsultaInput.model_validate(payload_dict)

        with st.spinner("Consultando processos monitorados..."):
            resultado_monitorados = consultar_processos_cached(payload_dict)

        st.session_state["resultado_monitorados"] = resultado_monitorados
        
    resultado_monitorados = st.session_state.get("resultado_monitorados") 
    
    if resultado_monitorados:
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
                    # data_ultima_atualizacao_fonte=(
                    #     processo.data_ultima_atualizacao_fonte.isoformat()
                    #     if processo.data_ultima_atualizacao_fonte
                    #     else None
                    # ),
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
                        "Data movimentação": atualizacao.data_movimentacao,
                        "Data": atualizacao.data_movimentacao.strftime("%d/%m/%Y %H:%M"),
                        "Descrição": atualizacao.descricao,
                        # "Última atualização": (
                        #     processo.data_ultima_atualizacao_fonte.strftime(
                        #         "%d/%m/%Y %H:%M"
                        #     )
                        #     if processo.data_ultima_atualizacao_fonte
                        #     else None
                        # ),
                    }
                )

        if not linhas_monitorados:
            st.info("Nenhuma movimentação encontrada para os processos monitorados.")
        else:
            df_monitorados_resultado = pd.DataFrame(linhas_monitorados)
            df_monitorados_resultado["Data movimentação"] = pd.to_datetime(
                df_monitorados_resultado["Data movimentação"],
                utc=True,
            )

            df_monitorados_resultado = df_monitorados_resultado.sort_values(
                by="Data movimentação",
                ascending=False,
            )
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

            df_novidades = df_monitorados_resultado[
                df_monitorados_resultado["Nova"] == "Sim"
            ].copy()
            df_monitorados_visual = df_monitorados_filtrado.drop(
                columns=["Data movimentação"],
            )


            if df_novidades.empty:
                st.info("Nenhuma novidade encontrada nesta consulta.")
            else:
                st.success(
                    f"{len(df_novidades)} nova(s) movimentação(ões) encontrada(s)."
                )
                df_novidades_visual = df_novidades.drop(
                    columns=["Data movimentação"],
                )

                st.download_button(
                    label="Baixar relatório de novidades em CSV",
                    data=df_novidades_visual.to_csv(index=False).encode("utf-8-sig"),
                    file_name="relatorio_novidades.csv",
                    mime="text/csv",
                )

            st.dataframe(
                df_monitorados_visual,
                use_container_width=True,
                hide_index=True,
            )

            csv_monitorados = df_monitorados_visual.to_csv(
                index=False
            ).encode("utf-8-sig")

            st.download_button(
                label="Baixar resultado dos monitorados em CSV",
                data=csv_monitorados,
                file_name="resultado_processos_monitorados.csv",
                mime="text/csv",
            )   