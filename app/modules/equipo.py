# app/modules/equipo.py
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

# Conversation states
DESCRIPTION, DURATION = range(2)

async def propose_activity_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation to propose an activity after a button press."""
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        "Por favor, describe la actividad que quieres proponer."
    )
    return DESCRIPTION

async def get_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the description and asks for the duration."""
    context.user_data['activity_description'] = update.message.text
    await update.message.reply_text(
        "Entendido. Ahora, por favor, indica la duración estimada en horas (ej. 2, 4.5)."
    )
    return DURATION

async def get_duration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the duration, confirms the proposal, and ends the conversation."""
    try:
        duration = float(update.message.text)
        context.user_data['activity_duration'] = duration
        description = context.user_data.get('activity_description', 'N/A')

        confirmation_text = (
            f"Gracias. Se ha enviado la siguiente propuesta para aprobación:\n\n"
            f"📝 *Actividad:* {description}\n"
            f"⏳ *Duración:* {duration} horas\n\n"
            "Recibirás una notificación cuando sea revisada."
        )
        # TODO: Send this proposal to the owner via webhook/db
        await update.message.reply_text(confirmation_text, parse_mode='Markdown')

        context.user_data.clear()
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("Por favor, introduce un número válido para la duración en horas.")
        return DURATION

async def cancel_proposal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await update.message.reply_text("La propuesta de actividad ha sido cancelada.")
    context.user_data.clear()
    return ConversationHandler.END

def view_requests_status():
    """
    Allows a team member to see the status of their requests.
    """
    # TODO: Fetch the status of recent requests
    return "Aquí está el estado de tus solicitudes recientes:\n\n- Grabación de proyecto (4h): Aprobado\n- Taller de guion (2h): Pendiente"
