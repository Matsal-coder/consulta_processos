from __future__ import annotations

import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path

from streamlit.web import cli as stcli


HOST = "localhost"
PORT = 8501
STARTUP_TIMEOUT_SECONDS = 30


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


def wait_for_streamlit() -> bool:
    deadline = time.time() + STARTUP_TIMEOUT_SECONDS

    while time.time() < deadline:
        try:
            with socket.create_connection((HOST, PORT), timeout=1):
                return True
        except OSError:
            time.sleep(0.5)

    return False


def open_browser_when_ready() -> None:
    if wait_for_streamlit():
        webbrowser.open(f"http://{HOST}:{PORT}")


def main() -> None:
    app_path = get_app_path()

    threading.Thread(
        target=open_browser_when_ready,
        daemon=True,
    ).start()

    sys.argv = [
        "streamlit",
        "run",
        str(app_path),
        "--global.developmentMode=false",
        "--server.headless=true",
        f"--server.port={PORT}",
    ]

    stcli.main()


if __name__ == "__main__":
    main()