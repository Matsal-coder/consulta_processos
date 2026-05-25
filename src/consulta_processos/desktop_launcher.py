from __future__ import annotations

import sys
import threading
import time
import webbrowser
from pathlib import Path

from streamlit.web import cli as stcli


def get_runtime_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)

    return Path(__file__).resolve().parents[2]


def open_browser() -> None:
    time.sleep(3)
    webbrowser.open("http://localhost:8501")


def main() -> None:
    try:
        runtime_root = get_runtime_root()
        app_path = runtime_root / "app.py"

        log_path = Path(sys.executable).parent / "juriscan_error.log"

        with log_path.open("w", encoding="utf-8") as log_file:
            log_file.write(f"runtime_root={runtime_root}\n")
            log_file.write(f"app_path={app_path}\n")
            log_file.write(f"app_exists={app_path.exists()}\n")

        if not app_path.exists():
            raise FileNotFoundError(f"Não encontrei o app.py em: {app_path}")

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

    except Exception as exc:
        log_path = Path(sys.executable).parent / "juriscan_error.log"

        with log_path.open("a", encoding="utf-8") as log_file:
            log_file.write("\nERRO:\n")
            log_file.write(repr(exc))

        raise


if __name__ == "__main__":
    main()