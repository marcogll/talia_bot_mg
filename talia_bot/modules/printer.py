# talia_bot/modules/printer.py
# This module will contain the SMTP/IMAP loop for the remote printing service.

import smtplib
import imaplib
import email
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from talia_bot.config import (
    SMTP_SERVER,
    SMTP_PORT,
    SMTP_USER,
    SMTP_PASS,
    IMAP_SERVER,
)
from talia_bot.modules.identity import is_admin

logger = logging.getLogger(__name__)

async def send_file_to_printer(file_path: str, user_id: int, file_name: str):
    """
    Sends a file to the printer via email.
    """
    if not is_admin(user_id):
        return "No tienes permiso para usar este comando."

    if not all([SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASS]):
        logger.error("Faltan una o más variables de entorno SMTP.")
        return "El servicio de impresión no está configurado correctamente."

    try:
        msg = MIMEMultipart()
        msg["From"] = SMTP_USER
        msg["To"] = SMTP_USER  # Sending to the printer's email address
        msg["Subject"] = f"Print Job from {user_id}: {file_name}"

        body = f"Nuevo trabajo de impresión enviado por el usuario {user_id}.\nNombre del archivo: {file_name}"
        msg.attach(MIMEText(body, "plain"))

        with open(file_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {file_name}",
        )
        msg.attach(part)

        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SMTP_USER, SMTP_PASS)
        text = msg.as_string()
        server.sendmail(SMTP_USER, SMTP_USER, text)
        server.quit()

        logger.info(f"Archivo {file_name} enviado a la impresora por el usuario {user_id}.")
        return f"Tu archivo '{file_name}' ha sido enviado a la impresora. Recibirás una notificación cuando el estado del trabajo cambie."

    except Exception as e:
        logger.error(f"Error al enviar el correo de impresión: {e}")
        return "Ocurrió un error al enviar el archivo a la impresora. Por favor, inténtalo de nuevo más tarde."


async def check_print_status(user_id: int):
    """
    Checks the status of print jobs by reading the inbox.
    """
    if not is_admin(user_id):
        return "No tienes permiso para usar este comando."

    if not all([IMAP_SERVER, SMTP_USER, SMTP_PASS]):
        logger.error("Faltan una o más variables de entorno IMAP.")
        return "El servicio de monitoreo de impresión no está configurado correctamente."

    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(SMTP_USER, SMTP_PASS)
        mail.select("inbox")

        status, messages = mail.search(None, "UNSEEN")
        if status != "OK":
            return "No se pudieron buscar los correos."

        email_ids = messages[0].split()
        if not email_ids:
            return "No hay actualizaciones de estado de impresión."

        statuses = []
        for e_id in email_ids:
            _, msg_data = mail.fetch(e_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject = msg["subject"].lower()
                    if "completed" in subject:
                        statuses.append(f"Trabajo de impresión completado: {msg['subject']}")
                    elif "failed" in subject:
                        statuses.append(f"Trabajo de impresión fallido: {msg['subject']}")
                    elif "received" in subject:
                        statuses.append(f"Trabajo de impresión recibido: {msg['subject']}")
                    else:
                        statuses.append(f"Nuevo correo: {msg['subject']}")

        mail.logout()

        if not statuses:
            return "No se encontraron actualizaciones de estado relevantes."

        return "\n".join(statuses)

    except Exception as e:
        logger.error(f"Error al revisar el estado de la impresión: {e}")
        return "Ocurrió un error al revisar el estado de la impresión."
