# app/main.py
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
from config import TELEGRAM_BOT_TOKEN
from permissions import get_user_role
from modules.onboarding import handle_start as onboarding_handle_start
from modules.onboarding import get_admin_secondary_menu
from modules.agenda import get_agenda
from modules.citas import request_appointment
from modules.equipo import (
    propose_activity_start,
    get_description,
    get_duration,
    cancel_proposal,
    view_requests_status,
    DESCRIPTION,
    DURATION,
)
from modules.aprobaciones import view_pending, handle_approval_action
from modules.servicios import get_service_info
from modules.admin import get_system_status
from modules.print import print_handler
from modules.create_tag import create_tag_conv_handler, create_tag_start
from modules.vikunja import vikunja_conv_handler, get_tasks as get_vikunja_tasks

from scheduler import schedule_daily_summary

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
        'view_pending': view_pending,
        'admin_menu': get_admin_secondary_menu,
    }

    if query.data in simple_handlers:
        handler = simple_handlers[query.data]
        logger.info(f"Ejecutando simple_handler para: {query.data}")
        if asyncio.iscoroutinefunction(handler):
            response_text = await handler()
        else:
            response_text = handler()
        logger.info(f"Respuesta obtenida para {query.data}")
        await query.edit_message_text(text=response_text, parse_mode='Markdown')
    elif query.data in complex_handlers:
        handler = complex_handlers[query.data]
        logger.info(f"Ejecutando complex_handler para: {query.data}")
        if asyncio.iscoroutinefunction(handler):
            response_text, reply_markup = await handler()
        else:
            response_text, reply_markup = handler()
        logger.info(f"Respuesta obtenida para {query.data}")
        await query.edit_message_text(text=response_text, reply_markup=reply_markup, parse_mode='Markdown')
    elif query.data.startswith(('approve:', 'reject:')):
        logger.info(f"Ejecutando acción de aprobación: {query.data}")
        response_text = handle_approval_action(query.data)
        await query.edit_message_text(text=response_text, parse_mode='Markdown')
    elif query.data == 'start_create_tag':
        await query.message.reply_text("Iniciando creación de tag...")
        return await create_tag_start(update, context)
    else:
        # Si no es ninguna de las acciones conocidas, asumimos que es para un ConversationHandler
        # y no hacemos nada aquí para no interferir.
        logger.warning(f"Consulta no manejada por el despachador principal: {query.data}")


def main() -> None:
    """Función principal que arranca el bot."""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN no está configurado en las variables de entorno.")
        return

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    schedule_daily_summary(application)

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(propose_activity_start, pattern='^propose_activity$')],
        states={
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_description)],
            DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_duration)],
        },
        fallbacks=[CommandHandler('cancel', cancel_proposal)],
        per_message=False
    )

    # El order de los handlers importa. El dispatcher debe ir después de los ConversationHandlers
    # para no interceptar sus callbacks.
    application.add_handler(conv_handler)
    application.add_handler(create_tag_conv_handler())
    application.add_handler(vikunja_conv_handler())
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("print", print_handler))
    application.add_handler(CallbackQueryHandler(button_dispatcher))

    logger.info("Iniciando Talía Bot...")
    application.run_polling()

if __name__ == "__main__":
    main()
