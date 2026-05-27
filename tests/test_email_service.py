import pytest

from consulta_processos.email_service import (
    enviar_email,
    is_email_enabled,
)


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
    monkeypatch.delenv(
        "EMAIL_ENABLED",
        raising=False,
    )

    assert is_email_enabled() is False


def test_enviar_email_sem_configuracao(
    monkeypatch,
):
    monkeypatch.delenv(
        "EMAIL_SMTP_HOST",
        raising=False,
    )

    with pytest.raises(ValueError):
        enviar_email(
            assunto="Teste",
            corpo_html="<p>Teste</p>",
        )