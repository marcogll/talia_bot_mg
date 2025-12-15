# app/scheduler.py

import schedule
import time
from datetime import datetime

from config import TIMEZONE

def send_daily_summary():
    """
    Sends the daily summary to the owner.
    """
    print(f"[{datetime.now()}] Sending daily summary...")
    # TODO: Implement the logic to fetch and send the summary

def main():
    """
    Main function to run the scheduler.
    """
    schedule.every().day.at("07:00").do(send_daily_summary)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
