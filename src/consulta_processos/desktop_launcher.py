from __future__ import annotations

import sys
import threading
import time
import webbrowser
from pathlib import Path

from streamlit.web import cli as stcli


def get_app_path() -> Path:
    candidates = []

    if getattr(sys, "frozen", False):
        candidates.extend(
            [
                Path(sys.executable).parent / "app.py",
                Path(sys.executable).parent / "_internal" / "app.py",
                Path(getattr(sys, "_MEIPASS", "")) / "app.py",
            ]
        )
    else:
        project_root = Path(__file__).resolve().parents[2]
        candidates.append(project_root / "app.py")

    for candidate in candidates:
        if candidate.exists():
            return candidate

    raise FileNotFoundError(
        "Não encontrei o app.py. Caminhos testados: "
        + ", ".join(str(path) for path in candidates)
    )


def open_browser() -> None:
    time.sleep(3)
    webbrowser.open("http://localhost:8501")


def main() -> None:
    app_path = get_app_path()

    threading.Thread(target=open_browser, daemon=True).start()

    sys.argv = [
        "streamlit",
        "run",
        str(app_path),
        "--global.developmentMode=false",
        "--server.headless=true",
        "--server.port=8501",
    ]

    stcli.main()


if __name__ == "__main__":
    main()