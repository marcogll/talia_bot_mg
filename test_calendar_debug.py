import datetime
import sys
import os

# Add app directory to path
sys.path.append(os.path.join(os.getcwd(), 'app'))

from google_calendar import get_events
from config import CALENDAR_ID

def test_get_events():
    print(f"Testing with CALENDAR_ID: {CALENDAR_ID}")
    now = datetime.datetime.now(datetime.timezone.utc)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + datetime.timedelta(days=1)
    
    print(f"Fetching events from {start_of_day.isoformat()} to {end_of_day.isoformat()}...")
    try:
        events = get_events(start_of_day, end_of_day)
        print(f"Found {len(events)} events.")
        for event in events:
            print(f"- {event.get('summary')} at {event['start'].get('dateTime', event['start'].get('date'))}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_get_events()
