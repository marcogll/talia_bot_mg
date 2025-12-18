# app/modules/vikunja.py
# Este módulo maneja la integración con Vikunja para la gestión de tareas.

import requests
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from app.config import VIKUNJA_API_URL, VIKUNJA_API_TOKEN
from app.permissions import is_admin

# Configuración del logger
logger = logging.getLogger(__name__)

# Definición de los estados de la conversación
SELECTING_ACTION, ADDING_TASK = range(2)

def get_vikunja_headers():
    """Devuelve los headers necesarios para la API de Vikunja."""
    return {
        "Authorization": f"Bearer {VIKUNJA_API_TOKEN}",
        "Content-Type": "application/json",
    }

async def vik_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Inicia la conversación de Vikunja y muestra el menú de acciones."""
    if not is_admin(update.effective_chat.id):
        await update.message.reply_text("No tienes permiso para usar este comando.")
        return ConversationHandler.END

    keyboard = [
        [InlineKeyboardButton("Ver Tareas", callback_data='view_tasks')],
        [InlineKeyboardButton("Añadir Tarea", callback_data='add_task')],
        [InlineKeyboardButton("Cancelar", callback_data='cancel')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Selecciona una opción para Vikunja:", reply_markup=reply_markup)
    return SELECTING_ACTION

async def view_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Muestra la lista de tareas de Vikunja."""
    query = update.callback_query
    await query.answer()

    if not VIKUNJA_API_TOKEN:
        await query.edit_message_text("Error: VIKUNJA_API_TOKEN no configurado.")
        return ConversationHandler.END

    try:
        response = requests.get(f"{VIKUNJA_API_URL}/projects/1/tasks", headers=get_vikunja_headers())
        response.raise_for_status()
        tasks = response.json()

        if not tasks:
            text = "No tienes tareas pendientes en Vikunja."
        else:
            text = "📋 *Tus Tareas en Vikunja*\n\n"
            for task in tasks[:10]:
                status = "✅" if task.get('done') else "⏳"
                text += f"{status} *{task.get('title')}*\n"
        
        await query.edit_message_text(text, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error al obtener tareas de Vikunja: {e}")
        await query.edit_message_text(f"Error al conectar con Vikunja: {e}")

    return ConversationHandler.END

async def request_task_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Solicita al usuario el título de la nueva tarea."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Por favor, introduce el título de la nueva tarea:")
    return ADDING_TASK

async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Añade una nueva tarea a Vikunja."""
    task_title = update.message.text

    if not VIKUNJA_API_TOKEN:
        await update.message.reply_text("Error: VIKUNJA_API_TOKEN no configurado.")
        return ConversationHandler.END

    try:
        # Usamos un project_id=1 hardcodeado como se definió en el plan
        data = {"title": task_title, "project_id": 1}
        response = requests.post(f"{VIKUNJA_API_URL}/tasks", headers=get_vikunja_headers(), json=data)
        response.raise_for_status()
        await update.message.reply_text(f"✅ Tarea añadida: *{task_title}*", parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error al añadir tarea a Vikunja: {e}")
        await update.message.reply_text(f"Error al añadir tarea: {e}")

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancela la conversación."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Operación cancelada.")
    return ConversationHandler.END

def vikunja_conv_handler():
    """Crea el ConversationHandler para el flujo de Vikunja."""
    return ConversationHandler(
        entry_points=[CommandHandler('vik', vik_start)],
        states={
            SELECTING_ACTION: [
                CallbackQueryHandler(view_tasks, pattern='^view_tasks$'),
                CallbackQueryHandler(request_task_title, pattern='^add_task$'),
                CallbackQueryHandler(cancel, pattern='^cancel$'),
            ],
            ADDING_TASK: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_task)
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
