from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from consulta_processos.paths import get_env_path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=get_env_path(),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    enable_local_history: bool = Field(
        default=False,
        alias="ENABLE_LOCAL_HISTORY",
    )

    consulta_processos_db_path: Path | None = Field(
        default=None,
        alias="CONSULTA_PROCESSOS_DB_PATH",
    )

    datajud_api_key: str = Field(
        default="",
        alias="DATAJUD_API_KEY",
    )

    email_enabled: bool = Field(
        default=False,
        alias="EMAIL_ENABLED",
    )
    email_smtp_host: str | None = Field(
        default=None,
        alias="EMAIL_SMTP_HOST",
    )
    email_smtp_port: int = Field(
        default=587,
        alias="EMAIL_SMTP_PORT",
    )
    email_username: str | None = Field(
        default=None,
        alias="EMAIL_USERNAME",
    )
    email_password: str | None = Field(
        default=None,
        alias="EMAIL_PASSWORD",
    )
    email_from: str | None = Field(
        default=None,
        alias="EMAIL_FROM",
    )
    email_to: str | None = Field(
        default=None,
        alias="EMAIL_TO",
    )


def get_settings() -> Settings:
    return Settings()