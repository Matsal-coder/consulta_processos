from fastapi import FastAPI

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
    return consultar_processos(payload)