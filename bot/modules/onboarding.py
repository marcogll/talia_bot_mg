# bot/modules/onboarding.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_dynamic_menu(user_role, flow_engine):
    """
    Creates a dynamic button menu based on the user's role.
    It filters the available flows and shows only the ones that:
    1. Match the user's role.
    2. Contain a 'trigger_button' key, indicating they can be started from a menu.
    """
    keyboard = []

    # Add role-specific static buttons first, if any.
    if user_role == "admin":
        keyboard.append([InlineKeyboardButton("👑 Revisar Pendientes", callback_data='view_pending')])
        keyboard.append([InlineKeyboardButton("📅 Agenda", callback_data='view_agenda')])

    # Dynamically add buttons from flows
    if flow_engine:
        for flow in flow_engine.flows:
            # Check if the flow is for the user's role and has a trigger button
            if flow.get("role") == user_role and "trigger_button" in flow and "name" in flow:
                button = InlineKeyboardButton(flow["name"], callback_data=flow["trigger_button"])
                keyboard.append([button])

    # Add secondary menu button for admins
    if user_role == "admin":
        keyboard.append([InlineKeyboardButton("▶️ Más opciones", callback_data='admin_menu')])

    return InlineKeyboardMarkup(keyboard)

def get_admin_secondary_menu():
    """Creates the secondary menu for Administrators."""
    text = "Aquí tienes más opciones de administración:"
    keyboard = [
        [InlineKeyboardButton("📋 Gestionar Tareas (Vikunja)", callback_data='manage_vikunja')],
        [InlineKeyboardButton("📊 Estado del sistema", callback_data='view_system_status')],
        [InlineKeyboardButton("👥 Gestionar Usuarios", callback_data='manage_users')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return text, reply_markup

def handle_start(user_role, flow_engine=None):
    """
    Decides which message and menu to show based on the user's role.
    """
    welcome_message = "Hola, soy Talía. ¿En qué puedo ayudarte hoy?"
    menu = get_dynamic_menu(user_role, flow_engine)
    return welcome_message, menu
