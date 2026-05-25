import json
from pathlib import Path
from consulta_processos.paths import get_config_dir

MONITORED_PROCESSES_FILENAME = "processos_monitorados.json"


def get_monitored_processes_path() -> Path:
    return get_config_dir() / MONITORED_PROCESSES_FILENAME


def carregar_processos_monitorados() -> list[dict]:
    path = get_monitored_processes_path()
    if not path.exists():
        return []

    content = path.read_text(
        encoding="utf-8"
    )

    if not content.strip():
        return []

    return json.loads(content)


def salvar_processos_monitorados(
    processos: list[dict],
) -> None:
    path = get_monitored_processes_path()
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
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

def remover_processo_monitorado(
    numero_processo: str,
    base: str,
) -> bool:
    processos = carregar_processos_monitorados()

    processos_filtrados = [
        processo
        for processo in processos
        if not (
            processo["numero_processo"] == numero_processo
            and processo["base"] == base
        )
    ]

    if len(processos_filtrados) == len(processos):
        return False

    salvar_processos_monitorados(
        processos_filtrados
    )

    return True