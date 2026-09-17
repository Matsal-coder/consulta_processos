from datetime import date

import pytest
from pydantic import ValidationError

from consulta_processos.models import ConsultaInput


def test_rejeita_lista_de_processos_vazia():
    with pytest.raises(ValidationError):
        ConsultaInput.model_validate({"processos": []})


def test_rejeita_numero_processo_vazio():
    with pytest.raises(ValidationError):
        ConsultaInput.model_validate(
            {
                "processos": [
                    {
                        "numero_processo": "",
                        "base": "tjrj_datajud",
                        "data_base": "2025-01-01",
                    }
                ]
            }
        )


def test_rejeita_data_base_futura():
    data_futura = date.today().replace(year=date.today().year + 1)

    with pytest.raises(ValidationError):
        ConsultaInput.model_validate(
            {
                "processos": [
                    {
                        "numero_processo": "0964024-67.2024.8.19.0001",
                        "base": "tjrj_datajud",
                        "data_base": data_futura.isoformat(),
                    }
                ]
            }
        )


def test_rejeita_base_inexistente():
    with pytest.raises(ValidationError):
        ConsultaInput.model_validate(
            {
                "processos": [
                    {
                        "numero_processo": "0964024-67.2024.8.19.0001",
                        "base": "base_inexistente",
                        "data_base": "2025-01-01",
                    }
                ]
            }
        )
