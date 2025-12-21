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
from talia_bot.modules.debug import print_handler
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import io
from talia_bot.modules.vikunja import get_projects, add_comment_to_task, update_task_status, get_project_tasks, create_task
from talia_bot.db import setup_database
from talia_bot.modules.flow_engine import FlowEngine
from talia_bot.modules.transcription import transcribe_audio
import uuid
from talia_bot.modules.llm_engine import analyze_client_pitch
from talia_bot.modules.calendar import create_event
from talia_bot.modules.mailer import send_email_with_attachment
from talia_bot.modules.imap_listener import check_for_confirmation
from talia_bot.config import ADMIN_ID, VIKUNJA_INBOX_PROJECT_ID

from talia_bot.scheduler import schedule_daily_summary

# Configuramos el sistema de logs para ver mensajes de estado en la consola
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Instanciamos el motor de flujos
flow_engine = FlowEngine()

async def send_step_message(update: Update, context: ContextTypes.DEFAULT_TYPE, step: dict, collected_data: dict = None):
    """
    Envía el mensaje de un paso del flujo, construyendo el teclado dinámicamente.
    """
    keyboard = []
    input_type = step.get("input_type")
    collected_data = collected_data or {}

    if input_type == "keyboard" and "options" in step:
        for option in step["options"]:
            keyboard.append([InlineKeyboardButton(option, callback_data=option)])
    elif input_type == "dynamic_keyboard_vikunja":
        projects = await get_projects()
        if projects:
            for project in projects:
                keyboard.append([InlineKeyboardButton(project['title'], callback_data=f"project_{project['id']}")])
        else:
            await update.effective_message.reply_text("No se pudieron cargar los proyectos de Vikunja.")
            return
    elif input_type == "dynamic_keyboard_vikunja_tasks":
        project_id_str = collected_data.get('PROJECT_SELECT', '').split('_')[-1]
        if project_id_str.isdigit():
            project_id = int(project_id_str)
            tasks = await get_project_tasks(project_id)
            if tasks:
                for task in tasks:
                    keyboard.append([InlineKeyboardButton(task['title'], callback_data=f"task_{task['id']}")])
            else:
                await update.effective_message.reply_text("Este proyecto no tiene tareas. Puedes añadir una o seleccionar otro proyecto.")
                # Aquí podríamos opcionalmente terminar el flujo o devolver al paso anterior.
                return
        else:
            await update.effective_message.reply_text("Error: No se pudo identificar el proyecto para buscar tareas.")
            return

    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None

    # Si la actualización es de un botón, edita el mensaje. Si no, envía uno nuevo.
    if update.callback_query:
        await update.callback_query.edit_message_text(
            text=step["question"], reply_markup=reply_markup, parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            text=step["question"], reply_markup=reply_markup, parse_mode='Markdown'
        )

async def universal_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler universal que gestiona todos los flujos de conversación.
    """
    user_id = update.effective_user.id
    user_role = get_user_role(user_id)

    state = flow_engine.get_conversation_state(user_id)

    if state:
        response_data = None
        if update.callback_query:
            response_data = update.callback_query.data
            await update.callback_query.answer()
        elif update.message and update.message.text:
            response_data = update.message.text
        elif update.message and update.message.voice:
            voice_file = await update.message.voice.get_file()
            file_buffer = io.BytesIO()
            await voice_file.download_to_memory(file_buffer)
            file_buffer.seek(0)
            file_buffer.name = "voice_message.oga"

            await update.message.reply_text("Transcribiendo audio... ⏳")
            response_data = await transcribe_audio(file_buffer)
            if response_data is None:
                await update.message.reply_text("Lo siento, no pude entender el audio. ¿Podrías intentarlo de nuevo?")
                return
        elif update.message and update.message.document:
            # Guardamos la información del archivo para el paso de resolución
            response_data = {
                "file_id": update.message.document.file_id,
                "file_name": update.message.document.file_name,
            }

        if response_data:
            result = flow_engine.handle_response(user_id, response_data)

            if result.get("status") == "in_progress":
                # Pasamos los datos recolectados para que el siguiente paso los pueda usar si es necesario
                current_state = flow_engine.get_conversation_state(user_id)
                await send_step_message(update, context, result["step"], current_state.get("collected_data"))
            elif result.get("status") == "complete":
                await handle_flow_resolution(update, context, result)
            elif result.get("status") == "error":
                await update.effective_message.reply_text(f"Error: {result.get('message', 'Ocurrió un error.')}")
        return

    trigger = None
    is_callback = False
    if update.callback_query:
        trigger = update.callback_query.data
        is_callback = True
        await update.callback_query.answer()
    elif update.message and update.message.text:
        trigger = update.message.text

    # Flujo automático para clientes
    if not trigger and user_role == 'client' and not state:
        flow_to_start = next((f for f in flow_engine.flows if f.get("trigger_automatic")), None)
        if flow_to_start:
             logger.info(f"Starting automatic flow '{flow_to_start['id']}' for client {user_id}")
             initial_step = flow_engine.start_flow(user_id, flow_to_start['id'])
             if initial_step:
                 await send_step_message(update, context, initial_step)
             return

    if trigger:
        for flow in flow_engine.flows:
            if trigger == flow.get('trigger_button') or trigger == flow.get('trigger_command'):
                logger.info(f"Starting flow '{flow['id']}' for user {user_id} via trigger '{trigger}'")
                initial_step = flow_engine.start_flow(user_id, flow['id'])
                if initial_step:
                    await send_step_message(update, context, initial_step)
                return

    # Si ninguna acción de flujo se disparó y es un callback, podría ser una acción del menú principal
    if is_callback:
        logger.info(f"Callback '{trigger}' no fue manejado por el motor de flujos. Pasando al dispatcher legado.")
        await button_dispatcher(update, context)


async def check_print_confirmation_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Job que se ejecuta para verificar la confirmación de impresión.
    """
    job = context.job
    user_id, job_id, file_name = job.data

    logger.info(f"Running print confirmation check for job_id: {job_id}")

    confirmation_data = await asyncio.to_thread(check_for_confirmation, job_id)

    if confirmation_data:
        await context.bot.send_message(chat_id=user_id, text=f"✅ ¡Éxito! Tu archivo '{file_name}' ha sido impreso correctamente.")
    else:
        await context.bot.send_message(chat_id=user_id, text=f"⚠️ El trabajo de impresión para '{file_name}' fue enviado, pero no he recibido una confirmación de la impresora. Por favor, verifica la bandeja de la impresora.")


async def handle_flow_resolution(update: Update, context: ContextTypes.DEFAULT_TYPE, result: dict):
    """
    Maneja la acción final de un flujo completado.
    """
    resolution_step = result.get("resolution")
    collected_data = result.get("data", {})

    if not resolution_step:
        logger.info(f"Flujo completado sin paso de resolución. Datos: {collected_data}")
        final_message = "Proceso completado. ✅"
        if update.callback_query:
            await update.callback_query.edit_message_text(final_message)
        else:
            await update.effective_message.reply_text(final_message)
        return

    resolution_type = resolution_step.get("input_type")
    final_message = resolution_step.get("question", "Hecho. ✅")

    logger.info(f"Resolviendo flujo con tipo '{resolution_type}' y datos: {collected_data}")

    # Lógica de resolución
    if resolution_type == "resolution_api_success":
        action = collected_data.get("ACTION_TYPE")
        task_id_str = collected_data.get("TASK_SELECT", "").split('_')[-1]
        update_content = collected_data.get("UPDATE_CONTENT")

        if task_id_str.isdigit():
            task_id = int(task_id_str)
            if action == "💬 Agregar Comentario":
                await add_comment_to_task(task_id=task_id, comment=update_content)
            elif action == "🔄 Actualizar Estatus":
                await update_task_status(task_id=task_id, status_text=update_content)
            elif action == "✅ Marcar Completado":
                 await update_task_status(task_id=task_id, is_done=True)

    elif resolution_type == "resolution_notify_admin":
        admin_id = context.bot_data.get("ADMIN_ID", ADMIN_ID) # Obtener ADMIN_ID de config
        if admin_id:
            user_info = (
                f"✨ **Nueva Solicitud de Onboarding** ✨\n\n"
                f"Un nuevo candidato ha completado el formulario:\n\n"
                f"👤 **Nombre:** {collected_data.get('ONBOARD_START', 'N/A')}\n"
                f"🏢 **Base:** {collected_data.get('ONBOARD_ORIGIN', 'N/A')}\n"
                f"📧 **Email:** {collected_data.get('ONBOARD_EMAIL', 'N/A')}\n"
                f"📱 **Teléfono:** {collected_data.get('ONBOARD_PHONE', 'N/A')}\n\n"
                f"Por favor, revisa y añade al usuario al sistema si es aprobado."
            )
            await context.bot.send_message(chat_id=admin_id, text=user_info, parse_mode='Markdown')

    elif resolution_type == "rag_analysis_resolution":
        pitch = collected_data.get("IDEA_PITCH")
        display_name = update.effective_user.full_name
        final_message = await analyze_client_pitch(pitch, display_name)

    elif resolution_type == "resolution_event_created":
        from dateutil.parser import parse
        from datetime import datetime, timedelta

        date_str = collected_data.get("BLOCK_DATE", "Hoy")
        time_str = collected_data.get("BLOCK_TIME", "")
        title = collected_data.get("BLOCK_TITLE", "Bloqueado por Talia")

        try:
            # Interpretar la fecha
            if date_str.lower() == 'hoy':
                start_date = datetime.now()
            elif date_str.lower() == 'mañana':
                start_date = datetime.now() + timedelta(days=1)
            else:
                start_date = parse(date_str)

            # Interpretar el rango de tiempo
            time_parts = [part.strip() for part in time_str.replace('a', '-').split('-')]
            start_time_obj = parse(time_parts[0])
            end_time_obj = parse(time_parts[1])

            start_time = start_date.replace(hour=start_time_obj.hour, minute=start_time_obj.minute, second=0, microsecond=0)
            end_time = start_date.replace(hour=end_time_obj.hour, minute=end_time_obj.minute, second=0, microsecond=0)

        except (ValueError, IndexError):
            final_message = "❌ Formato de fecha u hora no reconocido. Por favor, usa algo como 'Hoy', 'Mañana', o '10am - 11am'."
            if update.callback_query:
                await update.callback_query.edit_message_text(final_message)
            else:
                await update.effective_message.reply_text(final_message)
            return

        event = await asyncio.to_thread(
            create_event,
            summary=title,
            start_time=start_time,
            end_time=end_time,
            attendees=[] # Añadir asistentes si fuera necesario
        )
        if not event:
            final_message = "❌ Hubo un error al crear el evento en el calendario."

    elif resolution_type == "resolution_saved":
        idea_action = collected_data.get("IDEA_ACTION")
        idea_content = collected_data.get('IDEA_CONTENT', 'N/A')

        if idea_action == "✅ Crear Tarea":
            if VIKUNJA_INBOX_PROJECT_ID:
                new_task = await create_task(
                    project_id=int(VIKUNJA_INBOX_PROJECT_ID),
                    title=idea_content
                )
                if new_task:
                    final_message = "Tarea creada exitosamente en tu bandeja de entrada de Vikunja."
                else:
                    final_message = "❌ Hubo un error al crear la tarea en Vikunja."
            else:
                final_message = "❌ Error: El ID del proyecto de bandeja de entrada de Vikunja no está configurado."

        elif idea_action == "📓 Guardar Nota":
            admin_id = ADMIN_ID
            idea_category = collected_data.get('IDEA_CATEGORY', 'N/A')
            message = (
                f"🧠 **Nueva Idea Capturada (Guardada como Nota)** 🧠\n\n"
                f"**Categoría:** {idea_category}\n\n"
                f"**Contenido:**\n{idea_content}"
            )
            await context.bot.send_message(chat_id=admin_id, text=message, parse_mode='Markdown')

    elif resolution_type == "resolution_email_sent":
        file_info = collected_data.get("UPLOAD_FILE")
        user_id = update.effective_user.id

        if isinstance(file_info, dict):
            file_id = file_info.get("file_id")
            file_name = file_info.get("file_name")

            if file_id and file_name:
                job_id = str(uuid.uuid4())
                subject_data = {
                    "job_id": job_id,
                    "telegram_id": user_id,
                    "filename": file_name
                }
                subject = f"DATA:{json.dumps(subject_data)}"

                file_obj = await context.bot.get_file(file_id)
                file_buffer = io.BytesIO()
                await file_obj.download_to_memory(file_buffer)
                file_buffer.seek(0)

                success = await send_email_with_attachment(
                    file_content=file_buffer.getvalue(),
                    filename=file_name,
                    subject=subject
                )

                if success:
                    final_message = f"Recibido. 📨\n\nTu trabajo de impresión ha sido enviado (Job ID: {job_id}). Te notificaré cuando la impresora confirme que ha sido impreso."

                    # Programar la verificación en segundo plano
                    context.job_queue.run_once(
                        check_print_confirmation_job,
                        when=60,  # segundos
                        data=(user_id, job_id, file_name),
                        name=f"print_job_{job_id}"
                    )
                else:
                    final_message = "❌ Hubo un error al enviar el archivo a la impresora."
            else:
                final_message = "❌ No se encontró la información del archivo."
        else:
            final_message = "❌ Error en el formato de los datos del archivo."

    elif resolution_type == "system_output_nfc":
        # Lógica para devolver un JSON con los datos para el tag NFC
        nfc_data = {
            "name": collected_data.get("WIZARD_START"),
            "employee_id": collected_data.get("NUM_EMP"),
            "branch": collected_data.get("SUCURSAL"),
            "telegram_id": collected_data.get("TELEGRAM_ID"),
        }
        final_message = f"```json\n{json.dumps(nfc_data, indent=2)}\n```"

    # Enviar el mensaje de confirmación final
    if update.callback_query:
        await update.callback_query.edit_message_text(final_message)
    else:
        await update.effective_message.reply_text(final_message)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Se ejecuta cuando el usuario escribe /start.
    Muestra un mensaje de bienvenida y un menú según el rol del usuario.
    """
    chat_id = update.effective_chat.id
    user_role = get_user_role(chat_id)

    logger.info(f"Usuario {chat_id} inició conversación con el rol: {user_role}")

    response_text, reply_markup = onboarding_handle_start(user_role)

    await update.message.reply_text(response_text, reply_markup=reply_markup, parse_mode='Markdown')

async def button_dispatcher(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Dispatcher legado para manejar botones que no inician flujos.
    """
    query = update.callback_query
    # No se necesita await query.answer() aquí porque ya se llamó en universal_handler
    logger.info(f"Dispatcher legado manejando consulta: {query.data}")

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
            if asyncio.iscoroutinefunction(handler):
                response_text = await handler()
            else:
                response_text = handler()
        elif query.data in complex_handlers:
            handler = complex_handlers[query.data]
            if asyncio.iscoroutinefunction(handler):
                response_text, reply_markup = await handler()
            else:
                response_text, reply_markup = handler()
        elif query.data.startswith(('approve:', 'reject:')):
            response_text = handle_approval_action(query.data)
        elif query.data == 'start_create_tag':
            response_text = "Para crear un tag, por favor usa el comando /create_tag."
        else:
            # Si llega aquí, es una acción que ni el motor ni el dispatcher conocen.
            await query.edit_message_text(text=f"Lo siento, la acción '{query.data}' no se reconoce.")
            return
    except Exception as exc:
        logger.exception(f"Error al procesar la acción {query.data} en el dispatcher legado: {exc}")
        response_text = "❌ Ocurrió un error al procesar tu solicitud."
        reply_markup = None

    await query.edit_message_text(text=response_text, reply_markup=reply_markup, parse_mode='Markdown')


def main() -> None:
    """Función principal que arranca el bot."""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN no está configurado en las variables de entorno.")
        return

    setup_database()

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    schedule_daily_summary(application)

    # Handlers principales
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("print", print_handler))

    # El handler universal para flujos (prioridad 0)
    application.add_handler(CallbackQueryHandler(universal_handler), group=0)

    # El dispatcher legado se mantiene para callbacks no manejados por el motor de flujos (prioridad 1)
    # Nota: La lógica de paso ahora está dentro del universal_handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, universal_handler), group=0)
    application.add_handler(MessageHandler(filters.VOICE, universal_handler), group=0)
    application.add_handler(MessageHandler(filters.Document.ALL, universal_handler), group=0)


    logger.info("Iniciando Talía Bot...")
    application.run_polling()

if __name__ == "__main__":
    main()
