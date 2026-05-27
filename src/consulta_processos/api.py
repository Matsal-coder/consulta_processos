from fastapi import FastAPI, HTTPException

from consulta_processos.exceptions import (
    BaseNaoSuportadaError,
    ConfiguracaoError,
    FonteExternaError,
)
from consulta_processos.models import ConsultaInput, ConsultaResultado
from consulta_processos.services import consultar_processos

app = FastAPI(
    title="Consulta Processos API",
    version="0.1.0",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/consultar-processos", response_model=ConsultaResultado)
def consultar_processos_endpoint(payload: ConsultaInput) -> ConsultaResultado:
    try:
        return consultar_processos(payload)
    except ConfiguracaoError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except BaseNaoSuportadaError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FonteExternaError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc