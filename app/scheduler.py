# app/scheduler.py

import datetime
import pytz
from telegram import Bot
from app.config import OWNER_CHAT_ID, TIMEZONE
from app.calendar import get_events_for_day


def format_event_time(start_time_str):
    """
    Formats the event start time into a user-friendly format.
    """
    if "T" in start_time_str:  # It's a dateTime
        dt_object = datetime.datetime.fromisoformat(start_time_str)
        return dt_object.strftime("%I:%M %p")
    else:  # It's a date
        return "All day"


async def send_daily_summary(context):
    """
    Sends the daily summary to the owner.
    """
    bot = context.bot
    today = datetime.datetime.now(pytz.timezone(TIMEZONE)).date()
    events = get_events_for_day(today)

    if not events:
        summary = "Good morning! You have no events scheduled for today."
    else:
        summary = "Good morning! Here is your schedule for today:\n\n"
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            formatted_time = format_event_time(start)
            summary += f"- {event['summary']} at {formatted_time}\n"

    await bot.send_message(chat_id=OWNER_CHAT_ID, text=summary)


def setup_scheduler(application):
    """
    Sets up the daily summary job.
    """
    tz = pytz.timezone(TIMEZONE)
    job_queue = application.job_queue
    job_queue.run_daily(
        send_daily_summary,
        time=datetime.time(hour=7, minute=0, tzinfo=tz),
        chat_id=OWNER_CHAT_ID,
        name="daily_summary",
    )
