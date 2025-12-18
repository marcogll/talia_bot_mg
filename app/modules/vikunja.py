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

from config import VIKUNJA_API_URL, VIKUNJA_API_TOKEN
from permissions import is_admin

# Configuración del logger
logger = logging.getLogger(__name__)

# Definición de los estados de la conversación para añadir y editar tareas
SELECTING_ACTION, ADDING_TASK, SELECTING_TASK_TO_EDIT, EDITING_TASK = range(4)

def get_vikunja_headers():
    """Devuelve los headers necesarios para la API de Vikunja."""
    return {
        "Authorization": f"Bearer {VIKUNJA_API_TOKEN}",
        "Content-Type": "application/json",
    }

def get_tasks():
    """
    Obtiene y formatea la lista de tareas de Vikunja.
    Esta función es síncrona y devuelve un string.
    """
    if not VIKUNJA_API_TOKEN:
        return "Error: VIKUNJA_API_TOKEN no configurado."

    try:
        response = requests.get(f"{VIKUNJA_API_URL}/projects/1/tasks", headers=get_vikunja_headers())
        response.raise_for_status()
        tasks = response.json()

        if not tasks:
            return "No tienes tareas pendientes en Vikunja."
        
        text = "📋 *Tus Tareas en Vikunja*\n\n"
        for task in sorted(tasks, key=lambda t: t.get('id', 0))[:10]:
            status = "✅" if task.get('done') else "⏳"
            text += f"{status} `{task.get('id')}`: *{task.get('title')}*\n"
        return text
    except Exception as e:
        logger.error(f"Error al obtener tareas de Vikunja: {e}")
        return f"Error al conectar con Vikunja: {e}"

async def vikunja_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Muestra el menú principal de acciones de Vikunja."""
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("Añadir Tarea", callback_data='add_task')],
        [InlineKeyboardButton("Editar Tarea", callback_data='edit_task_start')],
        [InlineKeyboardButton("Volver", callback_data='cancel')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    tasks_list = get_tasks()
    await query.edit_message_text(text=f"{tasks_list}\n\nSelecciona una acción:", reply_markup=reply_markup, parse_mode='Markdown')
    return SELECTING_ACTION

async def request_task_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Solicita al usuario el título de la nueva tarea."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Por favor, introduce el título de la nueva tarea:")
    return ADDING_TASK

async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Añade una nueva tarea a Vikunja."""
    task_title = update.message.text
    try:
        data = {"title": task_title, "project_id": 1}
        response = requests.post(f"{VIKUNJA_API_URL}/tasks", headers=get_vikunja_headers(), json=data)
        response.raise_for_status()
        await update.message.reply_text(f"✅ Tarea añadida: *{task_title}*", parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error al añadir tarea a Vikunja: {e}")
        await update.message.reply_text(f"Error al añadir tarea: {e}")

    return ConversationHandler.END

async def select_task_to_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Muestra los botones para seleccionar qué tarea editar."""
    query = update.callback_query
    await query.answer()

    try:
        response = requests.get(f"{VIKUNJA_API_URL}/projects/1/tasks", headers=get_vikunja_headers())
        response.raise_for_status()
        tasks = [task for task in response.json() if not task.get('done')]

        if not tasks:
            await query.edit_message_text("No hay tareas pendientes para editar.")
            return ConversationHandler.END

        keyboard = []
        for task in sorted(tasks, key=lambda t: t.get('id', 0))[:10]:
            keyboard.append([InlineKeyboardButton(
                f"{task.get('id')}: {task.get('title')}",
                callback_data=f"edit_task:{task.get('id')}"
            )])
        keyboard.append([InlineKeyboardButton("Cancelar", callback_data='cancel')])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Selecciona la tarea que quieres editar:", reply_markup=reply_markup)
        return SELECTING_TASK_TO_EDIT
    except Exception as e:
        logger.error(f"Error al obtener tareas para editar: {e}")
        await query.edit_message_text("Error al obtener la lista de tareas.")
        return ConversationHandler.END

async def request_new_task_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Solicita el nuevo título para la tarea seleccionada."""
    query = update.callback_query
    await query.answer()

    task_id = query.data.split(':')[1]
    context.user_data['task_id_to_edit'] = task_id

    await query.edit_message_text(f"Introduce el nuevo título para la tarea `{task_id}`:", parse_mode='Markdown')
    return EDITING_TASK

async def edit_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Actualiza el título de una tarea en Vikunja."""
    new_title = update.message.text
    task_id = context.user_data.get('task_id_to_edit')

    if not task_id:
        await update.message.reply_text("Error: No se encontró el ID de la tarea a editar.")
        return ConversationHandler.END

    try:
        data = {"title": new_title}
        response = requests.put(f"{VIKUNJA_API_URL}/tasks/{task_id}", headers=get_vikunja_headers(), json=data)
        response.raise_for_status()
        await update.message.reply_text(f"✅ Tarea `{task_id}` actualizada a *{new_title}*", parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error al editar la tarea {task_id}: {e}")
        await update.message.reply_text("Error al actualizar la tarea.")
    finally:
        del context.user_data['task_id_to_edit']

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancela la conversación actual."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Operación cancelada.")
    return ConversationHandler.END

def vikunja_conv_handler():
    """Crea el ConversationHandler para el flujo de Vikunja."""
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(vikunja_menu, pattern='^manage_vikunja$')],
        states={
            SELECTING_ACTION: [
                CallbackQueryHandler(request_task_title, pattern='^add_task$'),
                CallbackQueryHandler(select_task_to_edit, pattern='^edit_task_start$'),
                CallbackQueryHandler(cancel, pattern='^cancel$'),
            ],
            ADDING_TASK: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_task)],
            SELECTING_TASK_TO_EDIT: [
                CallbackQueryHandler(request_new_task_title, pattern=r'^edit_task:\d+$'),
                CallbackQueryHandler(cancel, pattern='^cancel$'),
            ],
            EDITING_TASK: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_task)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
