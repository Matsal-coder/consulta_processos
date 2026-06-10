from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage

from consulta_processos.exceptions import ConfiguracaoError
from consulta_processos.settings import Settings, get_settings

logger = logging.getLogger(__name__)


def is_email_enabled() -> bool:
    return get_settings().email_enabled


def validate_email_configuration(settings: Settings) -> None:
    missing_fields = []

    if not settings.email_smtp_host:
        missing_fields.append("EMAIL_SMTP_HOST")

    if not settings.email_username:
        missing_fields.append("EMAIL_USERNAME")

    if not settings.email_password:
        missing_fields.append("EMAIL_PASSWORD")

    if not settings.email_from:
        missing_fields.append("EMAIL_FROM")

    if not settings.email_to:
        missing_fields.append("EMAIL_TO")

    if missing_fields:
        raise ConfiguracaoError(
            "Configurações de email incompletas. "
            f"Campos ausentes: {', '.join(missing_fields)}."
        )


def enviar_email(
    assunto: str,
    corpo_html: str,
) -> None:
    settings = get_settings()

    if not settings.email_enabled:
        logger.info("Email automático desabilitado.")
        return

    validate_email_configuration(settings)

    smtp_host = settings.email_smtp_host
    smtp_port = settings.email_smtp_port
    username = settings.email_username
    password = settings.email_password
    email_from = settings.email_from
    email_to = settings.email_to

    message = EmailMessage()
    message["Subject"] = assunto
    message["From"] = email_from
    message["To"] = email_to

    message.set_content(
        "Seu cliente de email não suporta HTML."
    )

    message.add_alternative(
        corpo_html,
        subtype="html",
    )

    logger.info(
        "Enviando email: assunto=%s destinatario=%s",
        assunto,
        email_to,
    )

    try:
        with smtplib.SMTP(
            smtp_host,
            smtp_port,
        ) as smtp:
            smtp.starttls()
            smtp.login(
                username,
                password,
            )
            smtp.send_message(message)
    except Exception:
        logger.exception(
            "Erro ao enviar email: destinatario=%s",
            email_to,
        )
        raise

    logger.info(
        "Email enviado com sucesso: destinatario=%s",
        email_to,
    )