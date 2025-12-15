# app/main.py
import logging
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

from config import TELEGRAM_BOT_TOKEN
from permissions import get_user_role
from modules.onboarding import handle_start as onboarding_handle_start
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

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message and menu when the /start command is issued."""
    chat_id = update.effective_chat.id
    user_role = get_user_role(chat_id)

    logger.info(f"User {chat_id} started conversation with role: {user_role}")

    response_text, reply_markup = onboarding_handle_start(user_role)

    await update.message.reply_text(response_text, reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and calls the appropriate module for simple actions."""
    query = update.callback_query
    await query.answer()
    logger.info(f"Button handler received callback query: {query.data}")

    response_text = "Acción no reconocida."
    reply_markup = None

    if query.data.startswith(('approve:', 'reject:')):
        response_text = handle_approval_action(query.data)
    elif query.data == 'view_pending':
        response_text, reply_markup = view_pending()
    else:
        simple_callbacks = {
            'view_agenda': get_agenda,
            'view_requests_status': view_requests_status,
            'schedule_appointment': request_appointment,
            'get_service_info': get_service_info,
        }
        handler_func = simple_callbacks.get(query.data)
        if handler_func:
            response_text = handler_func()

    await query.edit_message_text(text=response_text, reply_markup=reply_markup, parse_mode='Markdown')

def main() -> None:
    """Start the bot."""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is not set in the environment variables.")
        return

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Conversation handler for proposing activities
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
    application.add_handler(CallbackQueryHandler(button))

    logger.info("Starting Talía Bot...")
    application.run_polling()

if __name__ == "__main__":
    main()
