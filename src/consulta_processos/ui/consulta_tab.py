import logging
from datetime import date

import pandas as pd
import streamlit as st
from pydantic import ValidationError

from consulta_processos.bases.catalog import FONTES_PROCESSUAIS
from consulta_processos.exceptions import ConsultaProcessosError
from consulta_processos.history_repository import (
    marcar_movimentacoes_novas,
    salvar_movimentacoes_do_processo,
)
from consulta_processos.models import ConsultaInput
from consulta_processos.monitoring_repository import (
    adicionar_processo_monitorado,
)
from consulta_processos.process_repository import (
    listar_clientes,
    salvar_processo,
)
from consulta_processos.ui.cached_services import consultar_processos_cached

logger = logging.getLogger(__name__)

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
        key: fonte.label
        for key, fonte in FONTES_PROCESSUAIS.items()
        if fonte.ativa
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

        try:
            payload_dict = {
                "processos": [
                    {
                        "numero_processo": numero,
                        "base": base,
                        "data_base": data_base.isoformat(),
                    }
                    for numero in numeros_processos
                ]
            }

            ConsultaInput.model_validate(payload_dict)

            with st.spinner("Consultando processos..."):
                resultado = consultar_processos_cached(payload_dict)

            st.session_state["resultado_consulta"] = resultado

        except ValidationError as exc:
            logger.warning("Erro de validação no payload de consulta", exc_info=exc)
            st.error("Revise os dados informados. Há campos inválidos.")
            st.exception(exc)

        except ConsultaProcessosError as exc:
            logger.warning("Erro controlado ao consultar processo", exc_info=exc)
            st.error(str(exc))

        except Exception as exc:
            logger.exception("Erro inesperado ao consultar processo")
            st.error(
                "Erro inesperado ao consultar o processo. "
                "Tente novamente ou revise a base selecionada."
            )
            st.exception(exc)

    resultado = st.session_state.get("resultado_consulta")

    if resultado:
        st.subheader("Resultado da consulta")

        linhas = []

        for processo in resultado.processos:
            st.write(f"### Processo {processo.numero_processo}")

            with st.expander(f"💾 Salvar / Monitorar processo {processo.numero_processo}"):
                clientes_existentes_salvar = listar_clientes()
                opcoes_cliente_salvar = clientes_existentes_salvar + ["Cadastrar novo cliente"]

                cliente_opcao_salvar = st.selectbox(
                    "Cliente",
                    options=opcoes_cliente_salvar or ["Cadastrar novo cliente"],
                    key=f"cliente_salvar_{processo.numero_processo}",
                )

                if cliente_opcao_salvar == "Cadastrar novo cliente":
                    cliente_salvar = st.text_input(
                        "Nome do novo cliente",
                        key=f"novo_cliente_salvar_{processo.numero_processo}",
                    )
                else:
                    cliente_salvar = cliente_opcao_salvar

                apelido = st.text_input(
                    "Apelido do processo (opcional)",
                    key=f"apelido_{processo.numero_processo}",
                )

                col_salvar, col_monitorar = st.columns(2)

                with col_salvar:
                    salvar = st.button(
                        "💾 Salvar processo",
                        key=f"salvar_processo_{processo.numero_processo}",
                    )

                with col_monitorar:
                    monitorar = st.button(
                        "⭐ Salvar e monitorar",
                        key=f"salvar_monitorar_{processo.numero_processo}",
                    )

                if salvar or monitorar:
                    if not cliente_salvar.strip():
                        st.error("Informe um cliente antes de salvar/monitorar.")
                    else:
                        criado = salvar_processo(
                            numero_processo=processo.numero_processo,
                            base=processo.base,
                            cliente=cliente_salvar,
                            apelido=apelido or None,
                        )

                        if monitorar:
                            foi_adicionado = adicionar_processo_monitorado(
                                cliente=cliente_salvar,
                                numero_processo=processo.numero_processo,
                                base=processo.base,
                            )

                            if foi_adicionado:
                                st.success("Processo salvo e adicionado aos monitorados.")
                            else:
                                st.info("Processo salvo. Ele já estava monitorado.")

                        elif criado:
                            st.success("Processo salvo com sucesso.")
                        else:
                            st.info("Processo já estava salvo.")
                        # =========================
                        # METADADOS
                        # =========================

                        st.write(
                            f"**Fonte:** {processo.fonte}"
                        )

                        if (
                            processo
                            .data_ultima_atualizacao_fonte
                        ):
                            data_formatada = (
                                processo
                                .data_ultima_atualizacao_fonte
                                .strftime("%d/%m/%Y %H:%M")
                            )

                            st.write(
                                f"**Última atualização da fonte:** "
                                f"{data_formatada}"
                            )

            if processo.observacao:
                st.warning(processo.observacao)

            # =========================
            # HISTÓRICO LOCAL
            # =========================

            if enable_local_history:
                processo.atualizacoes = (
                    marcar_movimentacoes_novas(
                        numero_processo=(
                            processo.numero_processo
                        ),
                        base=processo.base,
                        atualizacoes=(
                            processo.atualizacoes
                        ),
                    )
                )

            if enable_local_history:
                novas = (
                    salvar_movimentacoes_do_processo(
                        numero_processo=(
                            processo.numero_processo
                        ),
                        base=processo.base,
                        atualizacoes=(
                            processo.atualizacoes
                        ),
                    )
                )

                st.success(
                    f"{novas} movimentação(ões) "
                    f"nova(s) salva(s) "
                    f"no histórico local."
                )

            # =========================
            # TABELA
            # =========================

            if not processo.atualizacoes:
                st.info(
                    "Nenhuma movimentação "
                    "encontrada a partir "
                    "da data-base informada."
                )

                continue

            for atualizacao in processo.atualizacoes:
                linhas.append(
                    {
                        "Processo": (
                            processo.numero_processo
                        ),
                        "Data movimentação": (
                            atualizacao
                            .data_movimentacao
                        ),
                        "Data": (
                            atualizacao
                            .data_movimentacao
                            .strftime(
                                "%d/%m/%Y %H:%M"
                            )
                        ),
                        "Descrição": (
                            atualizacao.descricao
                        ),
                        "Nova": (
                            "Sim"
                            if atualizacao.nova is True
                            else "Não"
                            if (
                                atualizacao.nova
                                is False
                            )
                            else (
                                "Histórico desativado"
                            )
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