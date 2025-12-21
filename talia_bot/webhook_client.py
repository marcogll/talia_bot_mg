# app/webhook_client.py
# Este script se encarga de enviar datos a servicios externos usando "webhooks".
# En este caso, se comunica con n8n.

import requests
from talia_bot.config import N8N_WEBHOOK_URL, N8N_TEST_WEBHOOK_URL

def send_webhook(event_data):
    """
    Envía datos de un evento al servicio n8n.
    Usa el webhook normal y, si falla o no existe, usa el de test como fallback.
    """
    # Intentar con el webhook principal
    if N8N_WEBHOOK_URL:
        try:
            print(f"Intentando enviar a webhook principal: {N8N_WEBHOOK_URL}")
            response = requests.post(N8N_WEBHOOK_URL, json=event_data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Fallo en webhook principal: {e}")

    # Fallback al webhook de test
    if N8N_TEST_WEBHOOK_URL:
        try:
            print(f"Intentando enviar a webhook de fallback (test): {N8N_TEST_WEBHOOK_URL}")
            response = requests.post(N8N_TEST_WEBHOOK_URL, json=event_data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Fallo en webhook de fallback: {e}")

    return None
