# app/modules/onboarding.py
# Este módulo maneja la primera interacción con el usuario (el comando /start).
# Se encarga de mostrar un menú diferente según quién sea el usuario (dueño, admin, equipo o cliente).

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_owner_menu():
    """Crea el menú de botones para el Dueño (Owner)."""
    keyboard = [
        [InlineKeyboardButton("📅 Ver mi agenda", callback_data='view_agenda')],
        [InlineKeyboardButton("⏳ Ver pendientes", callback_data='view_pending')],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_menu():
    """Crea el menú de botones principal para los Administradores."""
    keyboard = [
        [InlineKeyboardButton("⏳ Revisar Pendientes", callback_data='view_pending')],
        [InlineKeyboardButton("📅 Agenda", callback_data='view_agenda')],
        [InlineKeyboardButton("🏷️ Crear Tag", callback_data='start_create_tag')],
        [InlineKeyboardButton("▶️ Más opciones", callback_data='admin_menu')],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_secondary_menu():
    """Crea el menú secundario para Administradores."""
    text = "Aquí tienes más opciones de administración:"
    keyboard = [
        [InlineKeyboardButton("📋 Gestionar Tareas (Vikunja)", callback_data='manage_vikunja')],
        [InlineKeyboardButton("📊 Estado del sistema", callback_data='view_system_status')],
        [InlineKeyboardButton("👥 Gestionar Usuarios", callback_data='manage_users')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return text, reply_markup

def get_team_menu():
    """Crea el menú de botones para los Miembros del Equipo."""
    keyboard = [
        [InlineKeyboardButton("🕒 Proponer actividad", callback_data='propose_activity')],
        [InlineKeyboardButton("📄 Ver estatus de solicitudes", callback_data='view_requests_status')],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_client_menu():
    """Crea el menú de botones para los Clientes externos."""
    keyboard = [
        [InlineKeyboardButton("🗓️ Agendar una cita", callback_data='schedule_appointment')],
        [InlineKeyboardButton("ℹ️ Información de servicios", callback_data='get_service_info')],
    ]
    return InlineKeyboardMarkup(keyboard)

def handle_start(user_role):
    """
    Decide qué mensaje y qué menú mostrar según el rol del usuario.
    """
    welcome_message = "Hola, soy Talía. ¿En qué puedo ayudarte hoy?"

    if user_role in ["owner", "admin"]:
        menu = get_admin_menu()
    elif user_role == "team":
        menu = get_team_menu()
    else:
        menu = get_client_menu()

    return welcome_message, menu
