# app/llm.py

from config import OPENAI_API_KEY

def get_smart_response(prompt):
    """
    Generates a smart response using an LLM.
    """

    if not OPENAI_API_KEY:
        return "OpenAI API key not configured."

    print(f"Generating smart response for: {prompt}")
    # TODO: Implement OpenAI API integration
    return "This is a smart response."
