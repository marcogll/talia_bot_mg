# talia_bot/config.py
# Este archivo se encarga de cargar todas las variables de entorno y configuraciones del bot.
# Las variables de entorno son valores que se guardan fuera del código por seguridad (como tokens y llaves API).

import os
from dotenv import load_dotenv
from pathlib import Path

# Cargar variables de entorno desde el archivo .env en la raíz del proyecto
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Token del bot de Telegram (obtenido de @BotFather)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# ID de chat del dueño del bot (para recibir notificaciones importantes)
ADMIN_ID = os.getenv("ADMIN_ID")

# Ruta al archivo de credenciales de la cuenta de servicio de Google
GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
if GOOGLE_SERVICE_ACCOUNT_FILE and not os.path.isabs(GOOGLE_SERVICE_ACCOUNT_FILE):
    GOOGLE_SERVICE_ACCOUNT_FILE = str(Path(__file__).parent.parent / GOOGLE_SERVICE_ACCOUNT_FILE)

# ID del calendario de Google que usará el bot
CALENDAR_ID = os.getenv("CALENDAR_ID")

# URL del webhook de n8n para enviar datos a otros servicios
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")
N8N_TEST_WEBHOOK_URL = os.getenv("N8N_TEST_WEBHOOK_URL")

# Configuración de Vikunja
VIKUNJA_API_URL = os.getenv("VIKUNJA_API_URL", "https://tasks.soul23.cloud/api/v1")
VIKUNJA_API_TOKEN = os.getenv("VIKUNJA_API_TOKEN")

# Llave de la API de OpenAI para usar modelos de lenguaje (como GPT)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Modelo de OpenAI a utilizar (ej. gpt-3.5-turbo, gpt-4)
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

# Hora del resumen diario (formato HH:MM)
DAILY_SUMMARY_TIME = os.getenv("DAILY_SUMMARY_TIME", "07:00")

# Enlace de Calendly para agendar citas
CALENDLY_LINK = os.getenv("CALENDLY_LINK", "https://calendly.com/user/appointment-link")

# Zona horaria por defecto para el manejo de fechas y horas
TIMEZONE = os.getenv("TIMEZONE", "America/Mexico_City")
