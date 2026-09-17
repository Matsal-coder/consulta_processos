from consulta_processos.jobs.email_monitorados_report import (
    montar_tabela_html,
)


def test_montar_tabela_html():
    html = montar_tabela_html(
        [
            {
                "cliente": "Cliente XPTO",
                "processo": "123",
                "base": "tjrj_datajud",
                "data": "01/01/2026",
                "descricao": "Nova movimentação",
            }
        ]
    )

    assert "Cliente XPTO" in html
    assert "123" in html
    assert "Nova movimentação" in html
    assert "Resumo por cliente" in html
