# app/llm.py

import openai
from app.config import OPENAI_API_KEY

def get_smart_response(prompt):
    """
    Generates a smart response using an LLM.
    """
    if not OPENAI_API_KEY:
        return "OpenAI API key not configured."

    openai.api_key = OPENAI_API_KEY

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"An error occurred with OpenAI: {e}")
        return "I'm sorry, I couldn't generate a response right now."
