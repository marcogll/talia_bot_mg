# talia_bot/modules/agenda.py
# Este módulo se encarga de manejar las peticiones relacionadas con la agenda.
# Permite obtener y mostrar las actividades programadas para el día.

import datetime
import logging
from talia_bot.modules.calendar import get_events
from talia_bot.config import WORK_GOOGLE_CALENDAR_ID, PERSONAL_GOOGLE_CALENDAR_ID

logger = logging.getLogger(__name__)

async def get_agenda():
    """
    Obtiene y muestra la agenda del usuario para el día actual desde Google Calendar.
    Diferencia entre eventos de trabajo (visibles) y personales (bloqueos).
    """
    try:
        logger.info("Obteniendo agenda...")
        now = datetime.datetime.now(datetime.timezone.utc)
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + datetime.timedelta(days=1)

        logger.info(f"Buscando eventos de trabajo en {WORK_GOOGLE_CALENDAR_ID} y personales en {PERSONAL_GOOGLE_CALENDAR_ID}")

        # Obtener eventos de trabajo (para mostrar)
        work_events = get_events(start_of_day, end_of_day, calendar_id=WORK_GOOGLE_CALENDAR_ID)

        # Obtener eventos personales (para comprobar bloqueos, no se muestran)
        personal_events = get_events(start_of_day, end_of_day, calendar_id=PERSONAL_GOOGLE_CALENDAR_ID)

        if not work_events and not personal_events:
            logger.info("No se encontraron eventos de ningún tipo.")
            return "📅 *Agenda para Hoy*\n\nTotalmente despejado. No hay eventos de trabajo ni personales."

        agenda_text = "📅 *Agenda para Hoy*\n\n"
        if not work_events:
            agenda_text += "No tienes eventos de trabajo programados para hoy.\n"
        else:
            for event in work_events:
                start = event["start"].get("dateTime", event["start"].get("date"))
                if "T" in start:
                    time_str = start.split("T")[1][:5]
                else:
                    time_str = "Todo el día"

                summary = event.get("summary", "(Sin título)")
                agenda_text += f"• *{time_str}* - {summary}\n"

        if personal_events:
            agenda_text += "\n🔒 Tienes tiempo personal bloqueado."

        logger.info("Agenda obtenida con éxito.")
        return agenda_text
    except Exception as e:
        logger.error(f"Error al obtener la agenda: {e}")
        return "❌ Error al obtener la agenda. Por favor, intenta de nuevo más tarde."
