# app/calendar.py

import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from app.config import GOOGLE_SERVICE_ACCOUNT_FILE, CALENDAR_ID

# Set up the Calendar API
SCOPES = ["https://www.googleapis.com/auth/calendar"]
creds = service_account.Credentials.from_service_account_file(
    GOOGLE_SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
service = build("calendar", "v3", credentials=creds)


def get_available_slots(
    start_time, end_time, duration_minutes=30, calendar_id=CALENDAR_ID
):
    """
    Fetches available calendar slots within a given time range.
    """
    try:
        time_min = start_time.isoformat()
        time_max = end_time.isoformat()

        freebusy_query = {
            "timeMin": time_min,
            "timeMax": time_max,
            "timeZone": "UTC",
            "items": [{"id": calendar_id}],
        }

        freebusy_result = service.freebusy().query(body=freebusy_query).execute()
        busy_slots = freebusy_result["calendars"][calendar_id]["busy"]

        # Create a list of all potential slots
        potential_slots = []
        current_time = start_time
        while current_time + datetime.timedelta(minutes=duration_minutes) <= end_time:
            potential_slots.append(
                (
                    current_time,
                    current_time + datetime.timedelta(minutes=duration_minutes),
                )
            )
            current_time += datetime.timedelta(minutes=duration_minutes)

        # Filter out busy slots
        available_slots = []
        for slot_start, slot_end in potential_slots:
            is_busy = False
            for busy in busy_slots:
                busy_start = datetime.datetime.fromisoformat(busy["start"])
                busy_end = datetime.datetime.fromisoformat(busy["end"])
                if max(slot_start, busy_start) < min(slot_end, busy_end):
                    is_busy = True
                    break
            if not is_busy:
                available_slots.append((slot_start, slot_end))

        return available_slots
    except HttpError as error:
        print(f"An error occurred: {error}")
        return []


def create_event(summary, start_time, end_time, attendees, calendar_id=CALENDAR_ID):
    """
    Creates a new event in the calendar.
    """
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
        created_event = (
            service.events().insert(calendarId=calendar_id, body=event).execute()
        )
        return created_event
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None


def get_events_for_day(date, calendar_id=CALENDAR_ID):
    """
    Fetches all events for a given day from the calendar.
    """
    try:
        time_min = date.isoformat() + "T00:00:00Z"
        time_max = date.isoformat() + "T23:59:59Z"

        events_result = (
            service.events()
            .list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        return events_result.get("items", [])
    except HttpError as error:
        print(f"An error occurred: {error}")
        return []
