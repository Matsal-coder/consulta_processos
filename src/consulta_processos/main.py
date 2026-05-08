import json
from pathlib import Path

from consulta_processos.models import ConsultaInput
from consulta_processos.services import consultar_processos


INPUT_PATH = Path("examples/input.json")
OUTPUT_PATH = Path("outputs/resultado.json")


def main() -> None:
    payload_dict = json.loads(INPUT_PATH.read_text(encoding="utf-8"))

    payload = ConsultaInput.model_validate(payload_dict)

    resultado = consultar_processos(payload)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    OUTPUT_PATH.write_text(
        resultado.model_dump_json(indent=2),
        encoding="utf-8",
    )

    print(f"Resultado salvo em: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()