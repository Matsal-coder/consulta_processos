from consulta_processos.datajud_client import DataJudClient


def test_limpar_numero_processo():
    resultado = DataJudClient._limpar_numero_processo(
        "0964024-67.2024.8.19.0001"
    )

    assert resultado == "09640246720248190001"