from datetime import date

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from consulta_processos.models import ConsultaInput
from consulta_processos.services import consultar_processos

load_dotenv()

st.set_page_config(
    page_title="Consulta de Processos",
    page_icon="⚖️",
    layout="wide",
)

st.title("⚖️ Consulta de Processos")
st.write("Consulte movimentações processuais usando a API pública do DataJud/CNJ.")

numeros_processos_texto = st.text_area(
    "Números dos processos",
    placeholder=(
        "Digite um processo por linha:\n"
        "0964024-67.2024.8.19.0001\n"
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

    st.subheader("Resultado da consulta")

    linhas = []

    for processo in resultado.processos:
        st.write(f"### Processo {processo.numero_processo}")
        st.write(f"**Fonte:** {processo.fonte}")

        if processo.data_ultima_atualizacao_fonte:
            st.write(
                "**Última atualização da fonte:** "
                f"{processo.data_ultima_atualizacao_fonte}"
            )

        if processo.observacao:
            st.warning(processo.observacao)

        if not processo.atualizacoes:
            st.info("Nenhuma movimentação encontrada a partir da data-base informada.")
            continue

        for atualizacao in processo.atualizacoes:
            linhas.append(
                {
                    "Processo": processo.numero_processo,
                    "Data": atualizacao.data_movimentacao.strftime("%d/%m/%Y %H:%M"),
                    "Descrição": atualizacao.descricao,
                    "Código": atualizacao.codigo,
                    "Órgão julgador": atualizacao.orgao_julgador,
                }
            )

    if linhas:
        df = pd.DataFrame(linhas)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )

        csv = df.to_csv(index=False).encode("utf-8-sig")

        st.download_button(
            label="Baixar resultado em CSV",
            data=csv,
            file_name="resultado_consulta_processos.csv",
            mime="text/csv",
        )