# app/google_calendar.py
# Este script maneja la integración con Google Calendar (Calendario de Google).
# Permite buscar espacios libres y crear eventos.

import datetime
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config import GOOGLE_SERVICE_ACCOUNT_FILE, CALENDAR_ID

logger = logging.getLogger(__name__)

# Configuración de los permisos (SCOPES) para acceder al calendario
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# Autenticación usando el archivo de cuenta de servicio (Service Account)
creds = service_account.Credentials.from_service_account_file(
    GOOGLE_SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

# Construcción del objeto 'service' que nos permite interactuar con la API de Google Calendar
service = build("calendar", "v3", credentials=creds)


def get_available_slots(
    start_time, end_time, duration_minutes=30, calendar_id=CALENDAR_ID
):
    """
    Busca espacios disponibles en el calendario dentro de un rango de tiempo.
    
    Parámetros:
    - start_time: Hora de inicio de la búsqueda.
    - end_time: Hora de fin de la búsqueda.
    - duration_minutes: Cuánto dura cada cita (por defecto 30 min).
    - calendar_id: El ID del calendario donde buscar.
    """
    try:
        # Convertimos las fechas a formato ISO (el que entiende Google)
        time_min = start_time.isoformat()
        time_max = end_time.isoformat()

        # Consultamos a Google qué horas están ocupadas (freebusy)
        freebusy_query = {
            "timeMin": time_min,
            "timeMax": time_max,
            "timeZone": "UTC",
            "items": [{"id": calendar_id}],
        }

        freebusy_result = service.freebusy().query(body=freebusy_query).execute()
        busy_slots = freebusy_result["calendars"][calendar_id]["busy"]

        # Creamos una lista de todos los posibles espacios (slots)
        potential_slots = []
        current_time = start_time
        while current_time + datetime.timedelta(minutes=duration_minutes) <= end_time:
            potential_slots.append(
                (
                    current_time,
                    current_time + datetime.timedelta(minutes=duration_minutes),
                )
            )
            # Avanzamos el tiempo para el siguiente espacio
            current_time += datetime.timedelta(minutes=duration_minutes)

        # Filtramos los espacios que chocan con horas ocupadas
        available_slots = []
        for slot_start, slot_end in potential_slots:
            is_busy = False
            for busy in busy_slots:
                busy_start = datetime.datetime.fromisoformat(busy["start"])
                busy_end = datetime.datetime.fromisoformat(busy["end"])
                # Si el espacio propuesto se cruza con uno ocupado, lo marcamos como ocupado
                if max(slot_start, busy_start) < min(slot_end, busy_end):
                    is_busy = True
                    break
            if not is_busy:
                available_slots.append((slot_start, slot_end))

        return available_slots
    except HttpError as error:
        print(f"Ocurrió un error con la API de Google: {error}")
        return []


def create_event(summary, start_time, end_time, attendees, calendar_id=CALENDAR_ID):
    """
    Crea un nuevo evento (cita) en el calendario.
    
    Parámetros:
    - summary: Título del evento.
    - start_time: Hora de inicio.
    - end_time: Hora de fin.
    - attendees: Lista de correos electrónicos de los asistentes.
    """
    # Definimos la estructura del evento según pide Google
    event = {
        "summary": summary,
        "start": {
            "dateTime": start_time.isoformat(),
            "timeZone": "UTC",
        },
        "end": {
            "dateTime": end_time.isoformat(),
            "timeZone": "UTC",
        },
        "attendees": [{"email": email} for email in attendees],
    }
    try:
        # Insertamos el evento en el calendario
        created_event = (
            service.events().insert(calendarId=calendar_id, body=event).execute()
        )
        return created_event
    except HttpError as error:
        print(f"Ocurrió un error al crear el evento: {error}")
        return None


def get_events(start_time, end_time, calendar_id=CALENDAR_ID):
    """
    Obtiene la lista de eventos entre dos momentos.
    """
    try:
        logger.info(f"Llamando a la API de Google Calendar para {calendar_id}")
        events_result = (
            service.events()
            .list(
                calendarId=calendar_id,
                timeMin=start_time.isoformat(),
                timeMax=end_time.isoformat(),
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])
        logger.info(f"Se obtuvieron {len(events)} eventos de la API.")
        return events
    except HttpError as error:
        logger.error(f"Ocurrió un error al obtener eventos: {error}")
        return []
    except Exception as e:
        logger.error(f"Error inesperado al obtener eventos: {e}")
        return []
