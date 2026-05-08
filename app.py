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

numero_processo = st.text_input(
    "Número do processo",
    placeholder="Ex: 0964024-67.2024.8.19.0001",
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
    if not numero_processo:
        st.error("Informe o número do processo.")
        st.stop()

    payload = ConsultaInput.model_validate(
        {
            "processos": [
                {
                    "numero_processo": numero_processo,
                    "base": base,
                    "data_base": data_base.isoformat(),
                }
            ]
        }
    )

    with st.spinner("Consultando processo..."):
        resultado = consultar_processos(payload)

    processo = resultado.processos[0]

    st.subheader("Resultado da consulta")

    st.write(f"**Processo:** {processo.numero_processo}")
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
    else:
        dados = [
            {
                "Data": atualizacao.data_movimentacao.strftime("%d/%m/%Y %H:%M"),
                "Descrição": atualizacao.descricao,
                "Código": atualizacao.codigo,
                "Órgão julgador": atualizacao.orgao_julgador,
            }
            for atualizacao in processo.atualizacoes
        ]

        df = pd.DataFrame(dados)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )