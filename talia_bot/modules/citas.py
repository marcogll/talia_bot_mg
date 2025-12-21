# app/modules/citas.py
# Este módulo maneja la programación de citas para los clientes.
# Permite a los usuarios obtener un enlace para agendar una reunión.

from talia_bot.config import CALENDLY_LINK

def request_appointment():
    """
    Proporciona al usuario un enlace para agendar una cita.
    
    Usa el enlace configurado en las variables de entorno.
    """
    response_text = (
        "Para agendar una cita, por favor utiliza el siguiente enlace: \n\n"
        f"[Agendar Cita]({CALENDLY_LINK})"
    )
    return response_text
