import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "src"))

from datetime import date

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from consulta_processos.models import ConsultaInput
from consulta_processos.services import consultar_processos

import os

from consulta_processos.database import initialize_database
from consulta_processos.history_repository import (
    listar_movimentacoes_salvas,
    marcar_movimentacoes_novas,
    salvar_movimentacoes_do_processo,
)
from consulta_processos.monitoring_repository import (
    adicionar_processo_monitorado,
    carregar_processos_monitorados,
    remover_processo_monitorado,
)

load_dotenv()

ENABLE_LOCAL_HISTORY = os.getenv("ENABLE_LOCAL_HISTORY", "false").lower() == "true"

if ENABLE_LOCAL_HISTORY:
    initialize_database()

st.set_page_config(
    page_title="Consulta de Processos",
    page_icon="⚖️",
    layout="wide",
)

st.title("⚖️ Consulta de Processos")

tab_consulta, tab_historico, tab_monitorados = st.tabs(
    [
        "🔎 Consulta",
        "🗂 Histórico local",
        "⭐ Monitorados",
    ]
)

with tab_consulta:
    st.write("Consulte movimentações processuais usando a API pública do DataJud/CNJ.")

    numeros_processos_texto = st.text_area(
        "Números dos processos",
        placeholder=(
            "Digite um processo por linha:\n"
            "1111111-11.1111.1.11.1111\n"
            "0000000-00.0000.0.00.0000"
        ),
        height=150,
    )

    data_base = st.date_input(
        "Buscar movimentações a partir de",
        value=date.today(),
    )

    base = st.selectbox(
        "Base de consulta",
        options=["tjrj_datajud"],
        format_func=lambda x: "TJRJ - DataJud" if x == "tjrj_datajud" else x,
    )

    consultar = st.button("Consultar processo", type="primary")

    if consultar:
        numeros_processos = [
            numero.strip()
            for numero in numeros_processos_texto.splitlines()
            if numero.strip()
        ]

        if not numeros_processos:
            st.error("Informe ao menos um número de processo.")
            st.stop()

        payload = ConsultaInput.model_validate(
            {
                "processos": [
                    {
                        "numero_processo": numero,
                        "base": base,
                        "data_base": data_base.isoformat(),
                    }
                    for numero in numeros_processos
                ]
            }
        )

        with st.spinner("Consultando processos..."):
            resultado = consultar_processos(payload)

        st.session_state["resultado_consulta"] = resultado

    resultado = st.session_state.get("resultado_consulta")

    if resultado:
        st.subheader("Resultado da consulta")

        linhas = []

        for processo in resultado.processos:    
            st.write(f"### Processo {processo.numero_processo}")
            col1, col2 = st.columns([4, 1])

            with col2:
                monitorado = st.button(
                    "⭐ Monitorar",
                    key=f"monitorar_{processo.numero_processo}",
                )

            if monitorado:
                foi_adicionado = adicionar_processo_monitorado(
                    numero_processo=processo.numero_processo,
                    base=processo.base,
                )

                if foi_adicionado:
                    st.success("Processo adicionado aos monitorados.")
                else:
                    st.info("Processo já estava monitorado.")
            st.write(f"**Fonte:** {processo.fonte}")

            if processo.data_ultima_atualizacao_fonte:
                data_formatada = (
                    processo.data_ultima_atualizacao_fonte
                    .strftime("%d/%m/%Y %H:%M")
                )

                st.write(
                    f"**Última atualização da fonte:** {data_formatada}"
                )

            if processo.observacao:
                st.warning(processo.observacao)

            if ENABLE_LOCAL_HISTORY:
                processo.atualizacoes = marcar_movimentacoes_novas(
                    numero_processo=processo.numero_processo,
                    base=processo.base,
                    atualizacoes=processo.atualizacoes,
                )

            if ENABLE_LOCAL_HISTORY:
                novas = salvar_movimentacoes_do_processo(
                    numero_processo=processo.numero_processo,
                    base=processo.base,
                    atualizacoes=processo.atualizacoes,
                    data_ultima_atualizacao_fonte=(
                        processo.data_ultima_atualizacao_fonte.isoformat()
                        if processo.data_ultima_atualizacao_fonte
                        else None
                    ),
                )

                st.success(f"{novas} movimentação(ões) nova(s) salva(s) no histórico local.")

            if not processo.atualizacoes:
                st.info("Nenhuma movimentação encontrada a partir da data-base informada.")
                continue

            for atualizacao in processo.atualizacoes:
                linhas.append(
                    {
                        "Processo": processo.numero_processo,
                        "Data movimentação": atualizacao.data_movimentacao,
                        "Data": atualizacao.data_movimentacao.strftime("%d/%m/%Y %H:%M"),
                        "Descrição": atualizacao.descricao,
                        "Código": atualizacao.codigo,
                        "Órgão julgador": atualizacao.orgao_julgador,
                        "Nova": (
                            "Sim"
                            if atualizacao.nova is True
                            else "Não"
                            if atualizacao.nova is False
                            else "Histórico desativado"
                        ),
                    }
                )

                if linhas:
                    df = pd.DataFrame(linhas)
                    df["Data movimentação"] = pd.to_datetime(
                        df["Data movimentação"],
                        utc=True,
                    )

                    df = df.sort_values(
                        by="Data movimentação",
                        ascending=False,
                    )

                    col1, col2, col3 = st.columns(3)

                    col1.metric("Processos consultados", len(resultado.processos))
                    col2.metric("Movimentações encontradas", len(df))

                    data_mais_recente = df["Data movimentação"].max()
                    col3.metric(
                        "Movimentação mais recente",
                        data_mais_recente.strftime("%d/%m/%Y %H:%M"),
                    )   

                    st.divider()

                    filtro_texto = st.text_input(
                        "Filtrar movimentações",
                        placeholder="Ex: Publicação, Petição, Conclusão...",
                    )

                    df_filtrado = df.copy()

                    if filtro_texto:
                        filtro = filtro_texto.lower()

                        df_filtrado = df_filtrado[
                            df_filtrado["Descrição"].str.lower().str.contains(filtro)
                            | df_filtrado["Processo"].str.lower().str.contains(filtro)
                            | df_filtrado["Órgão julgador"].fillna("").str.lower().str.contains(filtro)
                            | df_filtrado["Código"].astype(str).str.contains(filtro)
                        ]
                    df_visual = df_filtrado.drop(
                        columns=["Data movimentação"],
                    )
                    st.dataframe(
                        df_visual,
                        use_container_width=True,
                        hide_index=True,
                    )

                    csv = df_visual.to_csv(index=False).encode("utf-8-sig")

                    st.download_button(
                        label="Baixar resultado filtrado em CSV",
                        data=csv,
                        file_name="resultado_consulta_processos.csv",
                        mime="text/csv",
                    )

with tab_historico:
    st.subheader("Histórico local de movimentações")

    if not ENABLE_LOCAL_HISTORY:
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
                df_historico["data_movimentacao"]
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

with tab_monitorados:
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
            if ENABLE_LOCAL_HISTORY:
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