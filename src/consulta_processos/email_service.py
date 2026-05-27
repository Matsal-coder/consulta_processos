from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage


def is_email_enabled() -> bool:
    return os.getenv("EMAIL_ENABLED", "false").lower() == "true"


def enviar_email(
    assunto: str,
    corpo_html: str,
) -> None:
    smtp_host = os.getenv("EMAIL_SMTP_HOST")
    smtp_port = int(os.getenv("EMAIL_SMTP_PORT", "587"))
    username = os.getenv("EMAIL_USERNAME")
    password = os.getenv("EMAIL_PASSWORD")
    email_from = os.getenv("EMAIL_FROM")
    email_to = os.getenv("EMAIL_TO")

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