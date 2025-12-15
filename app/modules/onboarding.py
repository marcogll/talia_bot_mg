# app/modules/onboarding.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_owner_menu():
    """Returns the main menu for the owner."""
    keyboard = [
        [InlineKeyboardButton("📅 Ver mi agenda", callback_data='view_agenda')],
        [InlineKeyboardButton("⏳ Ver pendientes", callback_data='view_pending')],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_menu():
    """Returns the main menu for an admin."""
    keyboard = [
        [InlineKeyboardButton("📊 Ver estado del sistema", callback_data='view_system_status')],
        [InlineKeyboardButton("👥 Gestionar usuarios", callback_data='manage_users')],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_team_menu():
    """Returns the main menu for a team member."""
    keyboard = [
        [InlineKeyboardButton("🕒 Proponer actividad", callback_data='propose_activity')],
        [InlineKeyboardButton("📄 Ver estatus de solicitudes", callback_data='view_requests_status')],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_client_menu():
    """Returns the main menu for a client."""
    keyboard = [
        [InlineKeyboardButton("🗓️ Agendar una cita", callback_data='schedule_appointment')],
        [InlineKeyboardButton("ℹ️ Información de servicios", callback_data='get_service_info')],
    ]
    return InlineKeyboardMarkup(keyboard)

def handle_start(user_role):
    """
    Handles the /start command and sends a role-based welcome message and menu.
    """
    welcome_message = "Hola, soy Talía. ¿En qué puedo ayudarte hoy?"

    if user_role == "owner":
        menu = get_owner_menu()
    elif user_role == "admin":
        menu = get_admin_menu()
    elif user_role == "team":
        menu = get_team_menu()
    else: # client
        menu = get_client_menu()

    return welcome_message, menu
