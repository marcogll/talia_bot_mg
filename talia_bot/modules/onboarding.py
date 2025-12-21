# talia_bot/modules/onboarding.py
# Este módulo maneja la primera interacción con el usuario (el comando /start).
# Se encarga de mostrar un menú diferente según quién sea el usuario (admin, crew o cliente).

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_admin_menu(flow_engine):
    """Crea el menú de botones principal para los Administradores."""
    keyboard = [
        [InlineKeyboardButton("👑 Revisar Pendientes", callback_data='view_pending')],
        [InlineKeyboardButton("📅 Agenda", callback_data='view_agenda')],
    ]

    # Dynamic buttons from flows
    if flow_engine:
        for flow in flow_engine.flows:
            if flow.get("role") == "admin" and "trigger_button" in flow and "name" in flow:
                button = InlineKeyboardButton(flow["name"], callback_data=flow["trigger_button"])
                keyboard.append([button])

    keyboard.append([InlineKeyboardButton("▶️ Más opciones", callback_data='admin_menu')])

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

def get_crew_menu():
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

def handle_start(user_role, flow_engine=None):
    """
    Decide qué mensaje y qué menú mostrar según el rol del usuario.
    """
    welcome_message = "Hola, soy Talía. ¿En qué puedo ayudarte hoy?"

    if user_role == "admin":
        menu = get_admin_menu(flow_engine)
    elif user_role == "crew":
        menu = get_crew_menu()
    else:
        menu = get_client_menu()

    return welcome_message, menu
