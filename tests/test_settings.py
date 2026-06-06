from consulta_processos.settings import (
    Settings,
)


def test_settings_email_enabled_true(
    monkeypatch,
):
    monkeypatch.setenv(
        "EMAIL_ENABLED",
        "true",
    )

    settings = Settings()

    assert settings.email_enabled is True


def test_settings_email_enabled_false(
    monkeypatch,
):
    monkeypatch.setenv(
        "EMAIL_ENABLED",
        "false",
    )

    settings = Settings()

    assert settings.email_enabled is False


def test_settings_db_path(
    monkeypatch,
):
    monkeypatch.setenv(
        "CONSULTA_PROCESSOS_DB_PATH",
        "test.db",
    )

    settings = Settings()

    assert str(
        settings.consulta_processos_db_path
    ) == "test.db"