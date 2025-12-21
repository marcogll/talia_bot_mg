# talia_bot/modules/sales_rag.py
# This module will contain the sales RAG flow for new clients.

import json
import logging
from talia_bot.modules.llm_engine import get_smart_response

logger = logging.getLogger(__name__)

def load_services_data():
    """Loads the services data from the JSON file."""
    try:
        with open("talia_bot/data/services.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("El archivo services.json no fue encontrado.")
        return []
    except json.JSONDecodeError:
        logger.error("Error al decodificar el archivo services.json.")
        return []

def find_relevant_services(user_query, services):
    """
    Finds relevant services based on the user's query.
    A simple keyword matching approach is used here.
    """
    query = user_query.lower()
    relevant_services = []
    for service in services:
        for keyword in service.get("keywords", []):
            if keyword in query:
                relevant_services.append(service)
                break  # Avoid adding the same service multiple times
    return relevant_services

def generate_sales_pitch(user_query, collected_data):
    """
    Generates a personalized sales pitch using the RAG approach.
    """
    services = load_services_data()
    relevant_services = find_relevant_services(user_query, services)

    if not relevant_services:
        # Fallback to all services if no specific keywords match
        context_str = "Aquí hay una descripción general de nuestros servicios:\n"
        for service in services:
            context_str += f"- **{service['service_name']}**: {service['description']}\n"
    else:
        context_str = "Según tus necesidades, aquí tienes algunos de nuestros servicios y ejemplos de lo que podemos hacer:\n"
        for service in relevant_services:
            context_str += f"\n**Servicio:** {service['service_name']}\n"
            context_str += f"*Descripción:* {service['description']}\n"
            if "work_examples" in service:
                context_str += "*Ejemplos de trabajo:*\n"
                for example in service["work_examples"]:
                    context_str += f"  - {example}\n"

    prompt = (
        f"Eres Talía, una asistente de ventas experta y amigable. Un cliente potencial llamado "
        f"{collected_data.get('CLIENT_NAME', 'cliente')} del sector "
        f"'{collected_data.get('CLIENT_INDUSTRY', 'no especificado')}' "
        f"ha descrito su proyecto o necesidad de la siguiente manera: '{user_query}'.\n\n"
        "A continuación, se presenta información sobre nuestros servicios que podría ser relevante para ellos:\n"
        f"{context_str}\n\n"
        "**Tu tarea es generar una respuesta personalizada que:**\n"
        "1.  Demuestre que has comprendido su necesidad específica.\n"
        "2.  Conecte de manera clara y directa su proyecto con nuestros servicios, utilizando los ejemplos de trabajo para ilustrar cómo podemos ayudar.\n"
        "3.  Mantenga un tono profesional, pero cercano y proactivo.\n"
        "4.  Finalice con una llamada a la acción clara, sugiriendo agendar una breve llamada para explorar la idea más a fondo.\n"
        "No te limites a listar los servicios; explica *cómo* se aplican a su caso."
    )

    return get_smart_response(prompt)
