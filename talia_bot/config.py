# talia_bot/config.py
# This file loads all environment variables and bot configurations.
# Environment variables are stored securely outside the code (e.g., in a .env file).

import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from the .env file in the project root
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# --- Telegram Configuration ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = os.getenv("TELEGRAM_OWNER_CHAT_ID")  # Renamed for consistency in the code

# --- Google Services ---
GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
if GOOGLE_SERVICE_ACCOUNT_FILE and not os.path.isabs(GOOGLE_SERVICE_ACCOUNT_FILE):
    GOOGLE_SERVICE_ACCOUNT_FILE = str(Path(__file__).parent.parent / GOOGLE_SERVICE_ACCOUNT_FILE)
CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")

# --- Webhooks (n8n) ---
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")
N8N_TEST_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_TEST_URL")

# --- AI Core ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
DAILY_SUMMARY_TIME = os.getenv("AI_DAILY_SUMMARY_TIME", "08:00")
TIMEZONE = os.getenv("TIMEZONE", "America/Monterrey")

# --- Scheduling ---
CALENDLY_LINK = os.getenv("CALENDLY_LINK")

# --- Vikunja (Task Management) ---
VIKUNJA_API_URL = os.getenv("VIKUNJA_BASE_URL")
VIKUNJA_API_TOKEN = os.getenv("VIKUNJA_TOKEN")

# --- Email Configuration (SMTP / IMAP) ---
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASSWORD")

IMAP_SERVER = os.getenv("IMAP_SERVER")
IMAP_USER = os.getenv("IMAP_USER")
IMAP_PASS = os.getenv("IMAP_PASSWORD")

# --- Printer (Epson Connect) ---
PRINTER_EMAIL = os.getenv("PRINTER_EMAIL")
