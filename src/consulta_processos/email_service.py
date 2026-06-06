from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage

from consulta_processos.settings import get_settings

logger = logging.getLogger(__name__)


def is_email_enabled() -> bool:
    return get_settings().email_enabled


def enviar_email(
    assunto: str,
    corpo_html: str,
) -> None:
    settings = get_settings()

    smtp_host = settings.email_smtp_host
    smtp_port = settings.email_smtp_port
    username = settings.email_username
    password = settings.email_password
    email_from = settings.email_from
    email_to = settings.email_to

    if not all(
        [
            smtp_host,
            username,
            password,
            email_from,
            email_to,
        ]
    ):
        raise ValueError(
            "Configurações de email incompletas. "
            "Verifique EMAIL_SMTP_HOST, EMAIL_USERNAME, "
            "EMAIL_PASSWORD, EMAIL_FROM e EMAIL_TO."
        )

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