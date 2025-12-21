# talia_bot/modules/llm_engine.py
# Este script se encarga de la comunicación con la inteligencia artificial de OpenAI.

import openai
from talia_bot.config import OPENAI_API_KEY, OPENAI_MODEL

def get_smart_response(prompt):
    """
    Genera una respuesta inteligente usando la API de OpenAI.

    Parámetros:
    - prompt: El texto o pregunta que le enviamos a la IA.
    """
    # Verificamos que tengamos la llave de la API configurada
    if not OPENAI_API_KEY:
        return "Error: La llave de la API de OpenAI no está configurada."

    try:
        # Creamos el cliente de OpenAI
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        # Solicitamos una respuesta al modelo configurado
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "Eres un asistente útil."},
                {"role": "user", "content": prompt},
            ],
        )
        # Devolvemos el contenido de la respuesta limpia (sin espacios extras)
        return response.choices[0].message.content.strip()
    except Exception as e:
        # Si algo sale mal, devolvemos el error
        return f"Ocurrió un error al comunicarse con OpenAI: {e}"

def transcribe_audio(audio_file_path):
    """
    Transcribes an audio file using OpenAI's Whisper model.

    Parameters:
    - audio_file_path: The path to the audio file.
    """
    if not OPENAI_API_KEY:
        return "Error: OPENAI_API_KEY is not configured."

    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)

        with open(audio_file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return transcript.text
    except Exception as e:
        return f"Error during audio transcription: {e}"
