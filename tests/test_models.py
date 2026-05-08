from consulta_processos.models import ConsultaInput


def test_validar_input():
    payload = {
        "processos": [
            {
                "numero_processo": "0000000-00.0000.0.00.0000",
                "base": "tjsp",
                "data_base": "2024-01-01"
            }
        ]
    }

    resultado = ConsultaInput.model_validate(payload)

    assert len(resultado.processos) == 1
    assert resultado.processos[0].base == "tjsp"