
import os
import requests
from dotenv import load_dotenv
from pathlib import Path

# Cargar variables de entorno
load_dotenv()

VIKUNJA_API_URL = os.getenv("VIKUNJA_API_URL", "https://tasks.soul23.cloud/api/v1")
VIKUNJA_API_TOKEN = os.getenv("VIKUNJA_API_TOKEN")

def test_vikunja_connection():
    if not VIKUNJA_API_TOKEN:
        print("Error: VIKUNJA_API_TOKEN no configurado en .env")
        return

    headers = {
        "Authorization": f"Bearer {VIKUNJA_API_TOKEN}",
        "Content-Type": "application/json"
    }

    print(f"Probando conexión a Vikunja: {VIKUNJA_API_URL}")
    try:
        # Intentar obtener información del usuario actual para validar el token
        response = requests.get(f"{VIKUNJA_API_URL}/user", headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            print(f"¡Conexión exitosa! Usuario: {user_data.get('username')}")
        else:
            print(f"Error de conexión: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error durante la prueba: {e}")

if __name__ == "__main__":
    test_vikunja_connection()
