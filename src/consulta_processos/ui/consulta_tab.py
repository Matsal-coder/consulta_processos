from datetime import date

import pandas as pd
import streamlit as st

from consulta_processos.models import ConsultaInput
from consulta_processos.services import consultar_processos
from consulta_processos.history_repository import (
    marcar_movimentacoes_novas,
    salvar_movimentacoes_do_processo
)
from consulta_processos.monitoring_repository import (
    adicionar_processo_monitorado
)

def render_consulta_tab(
    enable_local_history: bool,
) -> None:
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

    BASE_OPTIONS = {
        "esaj_tjsp": "TJSP - e-SAJ",
        "esaj_tjam": "TJAM - e-SAJ",
        "datajud_tjrj": "TJRJ - DataJud",
        "datajud_tjsp": "TJSP - DataJud",
        "datajud_tjes": "TJES - DataJud",
        "datajud_tjba": "TJBA - DataJud",
        "datajud_tjam": "TJAM - DataJud",
        "datajud_trf2": "TRF2 - DataJud",
    }

    base = st.selectbox(
        "Base de consulta",
        options=list(BASE_OPTIONS.keys()),
        format_func=lambda x: BASE_OPTIONS[x],
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

            if enable_local_history:
                processo.atualizacoes = marcar_movimentacoes_novas(
                    numero_processo=processo.numero_processo,
                    base=processo.base,
                    atualizacoes=processo.atualizacoes,
                )

            if enable_local_history:
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