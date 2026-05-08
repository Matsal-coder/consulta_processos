import json
from pathlib import Path


MONITORED_PROCESSES_PATH = Path(
    "config/processos_monitorados.json"
)


def carregar_processos_monitorados() -> list[dict]:
    if not MONITORED_PROCESSES_PATH.exists():
        return []

    content = MONITORED_PROCESSES_PATH.read_text(
        encoding="utf-8"
    )

    if not content.strip():
        return []

    return json.loads(content)


def salvar_processos_monitorados(
    processos: list[dict],
) -> None:
    MONITORED_PROCESSES_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    MONITORED_PROCESSES_PATH.write_text(
        json.dumps(
            processos,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def adicionar_processo_monitorado(
    numero_processo: str,
    base: str,
) -> bool:
    processos = carregar_processos_monitorados()

    existe = any(
        p["numero_processo"] == numero_processo
        and p["base"] == base
        for p in processos
    )

    if existe:
        return False

    processos.append(
        {
            "numero_processo": numero_processo,
            "base": base,
        }
    )

    salvar_processos_monitorados(processos)

    return True