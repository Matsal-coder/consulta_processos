import streamlit as st

from consulta_processos.models import ConsultaInput, ConsultaResultado
from consulta_processos.services import consultar_processos


@st.cache_data(
    ttl=300,
    show_spinner=False,
)
def consultar_processos_cached(
    payload_dict: dict,
) -> ConsultaResultado:
    payload = ConsultaInput.model_validate(payload_dict)

    return consultar_processos(payload)