import pytest

from consulta_processos.email_service import (
    enviar_email,
    is_email_enabled,
)
from consulta_processos.exceptions import ConfiguracaoError


def test_is_email_enabled_true(
    monkeypatch,
):
    monkeypatch.setenv(
        "EMAIL_ENABLED",
        "true",
    )

    assert is_email_enabled() is True


def test_is_email_enabled_false(
    monkeypatch,
):
    monkeypatch.setenv(
        "EMAIL_ENABLED",
        "false",
    )

    assert is_email_enabled() is False


def test_enviar_email_sem_configuracao(
    monkeypatch,
):
    monkeypatch.setenv(
        "EMAIL_ENABLED",
        "true",
    )
    monkeypatch.setenv(
        "EMAIL_SMTP_HOST",
        "",
    )

    with pytest.raises(ConfiguracaoError):
        enviar_email(
            assunto="Teste",
            corpo_html="<p>Teste</p>",
        )
