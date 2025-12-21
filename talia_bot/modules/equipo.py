# app/modules/equipo.py
# Este módulo contiene funciones para los miembros autorizados del equipo.
# Incluye un flujo para proponer actividades que el dueño debe aprobar.

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

# Definimos los estados para la conversación de propuesta de actividad.
DESCRIPTION, DURATION = range(2)

async def propose_activity_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print("--- PROPOSE ACTIVITY START CALLED ---")
    """
    Inicia el proceso para que un miembro del equipo proponga una actividad.
    Se activa cuando se pulsa el botón correspondiente.
    """
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        "Por favor, describe la actividad que quieres proponer."
    )
    # Siguiente paso: DESCRIPTION
    return DESCRIPTION

async def get_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Guarda la descripción de la actividad y pide la duración.
    """
    context.user_data['activity_description'] = update.message.text
    await update.message.reply_text(
        "Entendido. Ahora, por favor, indica la duración estimada en horas (ej. 2, 4.5)."
    )
    # Siguiente paso: DURATION
    return DURATION

async def get_duration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Guarda la duración, confirma la propuesta y termina la conversación.
    """
    try:
        # Intentamos convertir el texto a un número decimal (float)
        duration = float(update.message.text)
        context.user_data['activity_duration'] = duration
        description = context.user_data.get('activity_description', 'N/A')

        confirmation_text = (
            f"Gracias. Se ha enviado la siguiente propuesta para aprobación:\n\n"
            f"📝 *Actividad:* {description}\n"
            f"⏳ *Duración:* {duration} horas\n\n"
            "Recibirás una notificación cuando sea revisada."
        )

        # TODO: Enviar esta propuesta al dueño (por webhook o base de datos).
        await update.message.reply_text(confirmation_text, parse_mode='Markdown')

        # Limpiamos los datos temporales
        context.user_data.clear()

        # Terminamos la conversación
        return ConversationHandler.END
    except ValueError:
        # Si el usuario no escribe un número válido, se lo pedimos de nuevo
        await update.message.reply_text("Por favor, introduce un número válido para la duración en horas.")
        return DURATION

async def cancel_proposal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Cancela el proceso de propuesta si el usuario escribe /cancel.
    """
    await update.message.reply_text("La propuesta de actividad ha sido cancelada.")
    context.user_data.clear()
    return ConversationHandler.END

def view_requests_status():
    """
    Permite a un miembro del equipo ver el estado de sus solicitudes recientes.
    
    Por ahora devuelve un estado de ejemplo fijo.
    """
    # TODO: Obtener el estado real desde una base de datos.
    return "Aquí está el estado de tus solicitudes recientes:\n\n- Grabación de proyecto (4h): Aprobado\n- Taller de guion (2h): Pendiente"
