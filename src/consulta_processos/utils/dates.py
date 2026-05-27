from __future__ import annotations

from datetime import date, datetime

FORMATOS_DATA = [
    "%d/%m/%Y",
    "%d/%m/%Y %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S.%f%z",
    "%Y-%m-%dT%H:%M:%S%z",
    "%Y-%m-%dT%H:%M:%S",
]


def parse_datetime(valor: str | None) -> datetime | None:
    if not valor:
        return None

    for formato in FORMATOS_DATA:
        try:
            return datetime.strptime(valor, formato)
        except ValueError:
            continue

    return None


def parse_date(valor: str | None) -> date | None:
    data = parse_datetime(valor)

    if data is None:
        return None

    return data.date()