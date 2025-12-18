# app/modules/create_tag.py
import base64
import json
import logging
from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

# Enable logging
logger = logging.getLogger(__name__)

# Define states for the conversation
NAME, NUM_EMP, SUCURSAL, TELEGRAM_ID = range(4)

async def create_tag_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation to create a new tag."""
    await update.message.reply_text("Vamos a crear un nuevo tag. Por favor, dime el nombre:")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the name and asks for the employee number."""
    context.user_data['name'] = update.message.text
    await update.message.reply_text("Gracias. Ahora, por favor, dime el número de empleado:")
    return NUM_EMP

async def get_num_emp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the employee number and asks for the branch."""
    context.user_data['num_emp'] = update.message.text
    await update.message.reply_text("Entendido. Ahora, por favor, dime la sucursal:")
    return SUCURSAL

async def get_sucursal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the branch and asks for the Telegram ID."""
    context.user_data['sucursal'] = update.message.text
    await update.message.reply_text("Perfecto. Finalmente, por favor, dime el ID de Telegram:")
    return TELEGRAM_ID

async def get_telegram_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the Telegram ID, generates the Base64 string, and ends the conversation."""
    context.user_data['telegram_id'] = update.message.text

    # Create the JSON object from the collected data
    tag_data = {
        "name": context.user_data.get('name'),
        "num_emp": context.user_data.get('num_emp'),
        "sucursal": context.user_data.get('sucursal'),
        "telegram_id": context.user_data.get('telegram_id'),
    }

    # Convert the dictionary to a JSON string
    json_string = json.dumps(tag_data)

    # Encode the JSON string to Base64
    base64_bytes = base64.b64encode(json_string.encode('utf-8'))
    base64_string = base64_bytes.decode('utf-8')

    await update.message.reply_text(f"¡Gracias! Aquí está tu tag en formato Base64:\n\n`{base64_string}`", parse_mode='Markdown')

    # Clean up user_data
    context.user_data.clear()

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await update.message.reply_text("Creación de tag cancelada.")
    context.user_data.clear()
    return ConversationHandler.END

def create_tag_conv_handler():
    """Creates a conversation handler for the /create_tag command."""
    return ConversationHandler(
        entry_points=[CommandHandler('create_tag', create_tag_start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            NUM_EMP: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_num_emp)],
            SUCURSAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_sucursal)],
            TELEGRAM_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_telegram_id)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        per_message=False
    )
