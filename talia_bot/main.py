# talia_bot/main.py
# Este es el archivo principal del bot. Aquí se inicia todo y se configuran los comandos.

import logging
import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Importamos las configuraciones y herramientas que creamos en otros archivos
from talia_bot.config import TELEGRAM_BOT_TOKEN
from talia_bot.modules.identity import get_user_role
from talia_bot.modules.onboarding import handle_start as onboarding_handle_start
from talia_bot.modules.onboarding import get_admin_secondary_menu
from talia_bot.modules.agenda import get_agenda
from talia_bot.modules.citas import request_appointment
from talia_bot.modules.equipo import (
    propose_activity_start,
    get_description,
    get_duration,
    cancel_proposal,
    view_requests_status,
    DESCRIPTION,
    DURATION,
)
from talia_bot.modules.aprobaciones import view_pending, handle_approval_action
from talia_bot.modules.servicios import get_service_info
from talia_bot.modules.admin import get_system_status
import os
from talia_bot.modules.debug import print_handler
from talia_bot.modules.create_tag import create_tag_conv_handler
from talia_bot.modules.vikunja import vikunja_conv_handler
from talia_bot.modules.printer import send_file_to_printer, check_print_status
from talia_bot.db import setup_database
from talia_bot.modules.flow_engine import FlowEngine

from talia_bot.scheduler import schedule_daily_summary

# Configuramos el sistema de logs para ver mensajes de estado en la consola
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Se ejecuta cuando el usuario escribe /start.
    Muestra un mensaje de bienvenida y un menú según el rol del usuario.
    """
    chat_id = update.effective_chat.id
    user_role = get_user_role(chat_id)

    logger.info(f"Usuario {chat_id} inició conversación con el rol: {user_role}")

    # Obtenemos el texto y los botones de bienvenida desde el módulo de onboarding
    response_text, reply_markup = onboarding_handle_start(user_role)

    # Respondemos al usuario
    await update.message.reply_text(response_text, reply_markup=reply_markup)


async def text_and_voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles text and voice messages for the flow engine."""
    user_id = update.effective_user.id
    flow_engine = context.bot_data["flow_engine"]

    state = flow_engine.get_conversation_state(user_id)
    if not state:
        # If there's no active conversation, treat it as a start command
        await start(update, context)
        return

    user_response = update.message.text
    if update.message.voice:
        # Here you would add the logic to transcribe the voice message
        # For now, we'll just use a placeholder
        user_response = "Voice message received (transcription not implemented yet)."

    result = flow_engine.handle_response(user_id, user_response)

    if result["status"] == "in_progress":
        await update.message.reply_text(result["step"]["question"])
    elif result["status"] == "complete":
        if "sales_pitch" in result:
            await update.message.reply_text(result["sales_pitch"])
        else:
            await update.message.reply_text("Gracias por completar el flujo.")
    elif result["status"] == "error":
        await update.message.reply_text(result["message"])


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles documents sent to the bot for printing."""
    document = update.message.document
    user_id = update.effective_user.id
    file = await context.bot.get_file(document.file_id)

    # Create a directory for temporary files if it doesn't exist
    temp_dir = 'temp_files'
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, document.file_name)

    await file.download_to_drive(file_path)

    response = await send_file_to_printer(file_path, user_id, document.file_name)
    await update.message.reply_text(response)

    # Clean up the downloaded file
    os.remove(file_path)


async def check_print_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Command to check print status."""
    user_id = update.effective_user.id
    response = await check_print_status(user_id)
    await update.message.reply_text(response)


async def button_dispatcher(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Esta función maneja los clics en los botones del menú.
    Dependiendo de qué botón se presione, ejecuta una acción diferente.
    """
    query = update.callback_query
    await query.answer()
    logger.info(f"El despachador recibió una consulta: {query.data}")

    response_text = "Acción no reconocida."
    reply_markup = None

    simple_handlers = {
        'view_agenda': get_agenda,
        'view_requests_status': view_requests_status,
        'schedule_appointment': request_appointment,
        'get_service_info': get_service_info,
        'view_system_status': get_system_status,
        'manage_users': lambda: "Función de gestión de usuarios no implementada.",
    }

    complex_handlers = {
        'admin_menu': get_admin_secondary_menu,
        'view_pending': view_pending,
    }

    try:
        if query.data in simple_handlers:
            handler = simple_handlers[query.data]
            logger.info(f"Ejecutando simple_handler para: {query.data}")
            if asyncio.iscoroutinefunction(handler):
                response_text = await handler()
            else:
                response_text = handler()
        elif query.data in complex_handlers:
            handler = complex_handlers[query.data]
            logger.info(f"Ejecutando complex_handler para: {query.data}")
            if asyncio.iscoroutinefunction(handler):
                response_text, reply_markup = await handler()
            else:
                response_text, reply_markup = handler()
        elif query.data.startswith(('approve:', 'reject:')):
            logger.info(f"Ejecutando acción de aprobación: {query.data}")
            response_text = handle_approval_action(query.data)
        elif query.data == 'start_create_tag':
            response_text = "Para crear un tag, por favor usa el comando /create_tag."
        else:
            logger.warning(f"Consulta no manejada por el despachador: {query.data}")
            await query.edit_message_text(text=response_text)
            return
    except Exception as exc:
        logger.exception(f"Error al procesar la acción {query.data}: {exc}")
        response_text = "❌ Ocurrió un error al procesar tu solicitud. Intenta de nuevo."
        reply_markup = None

    # Check if the button is a flow trigger
    flow_engine = context.bot_data["flow_engine"]
    flow_to_start = next((flow for flow in flow_engine.flows if flow.get("trigger_button") == query.data), None)

    if flow_to_start:
        initial_step = flow_engine.start_flow(update.effective_user.id, flow_to_start["id"])
        if initial_step:
            await query.edit_message_text(text=initial_step["question"])
        return

    await query.edit_message_text(text=response_text, reply_markup=reply_markup, parse_mode='Markdown')

def main() -> None:
    """Función principal que arranca el bot."""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN no está configurado en las variables de entorno.")
        return

    setup_database()

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Instantiate and store the flow engine in bot_data
    flow_engine = FlowEngine()
    application.bot_data["flow_engine"] = flow_engine

    schedule_daily_summary(application)

    # El orden de los handlers es crucial para que las conversaciones funcionen.
    application.add_handler(create_tag_conv_handler())
    application.add_handler(vikunja_conv_handler())

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(propose_activity_start, pattern='^propose_activity$')],
        states={
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_description)],
            DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_duration)],
        },
        fallbacks=[CommandHandler('cancel', cancel_proposal)],
        per_message=False
    )
    application.add_handler(conv_handler)

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("print", print_handler))
    application.add_handler(CommandHandler("check_print_status", check_print_status_command))

    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND | filters.VOICE, text_and_voice_handler))

    application.add_handler(CallbackQueryHandler(button_dispatcher))

    logger.info("Iniciando Talía Bot...")
    application.run_polling()

if __name__ == "__main__":
    main()
