from datetime import date

from playwright.sync_api import sync_playwright

from consulta_processos.models import AtualizacaoProcesso


URL_TJRJ_EPROC = (
    "https://eproc1g-cp.tjrj.jus.br/eproc/"
    "externo_controlador.php?acao=processo_consulta_publica"
)


def consultar_processo_tjrj_eproc(
    numero_processo: str,
    data_base: date,
) -> list[AtualizacaoProcesso]:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto(URL_TJRJ_EPROC)

        # Próximo passo: ajustar o seletor real do campo
        page.fill("input[name='num_processo']", numero_processo)

        # Próximo passo: ajustar o seletor real do botão
        page.click("input[type='submit']")

        page.wait_for_load_state("networkidle")

        print(page.title())
        print(page.content()[:2000])

        browser.close()

    return []