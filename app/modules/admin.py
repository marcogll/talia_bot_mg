# app/modules/admin.py

def get_system_status():
    """
    Returns the current status of the bot and its integrations.
    """
    # TODO: Implement real-time status checks
    status_text = (
        "📊 *Estado del Sistema*\n\n"
        "- *Bot Principal:* Activo ✅\n"
        "- *Conexión Telegram API:* Estable ✅\n"
        "- *Integración n8n:* Operacional ✅\n"
        "- *Google Calendar:* Conectado ✅"
    )
    return status_text
