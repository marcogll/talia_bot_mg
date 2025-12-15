# app/modules/aprobaciones.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_approval_menu(request_id):
    """Returns an inline keyboard for approving or rejecting a request."""
    keyboard = [
        [
            InlineKeyboardButton("✅ Aprobar", callback_data=f'approve:{request_id}'),
            InlineKeyboardButton("❌ Rechazar", callback_data=f'reject:{request_id}'),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def view_pending():
    """
    Shows the owner a list of pending requests with approval buttons.
    For now, it returns a hardcoded list of proposals.
    """
    # TODO: Fetch pending requests from a database or webhook events
    proposals = [
        {"id": "prop_001", "desc": "Grabación de proyecto", "duration": 4, "user": "Equipo A"},
        {"id": "prop_002", "desc": "Taller de guion", "duration": 2, "user": "Equipo B"},
    ]

    if not proposals:
        return "No hay solicitudes pendientes.", None

    # For simplicity, we'll just show the first pending proposal
    proposal = proposals[0]

    text = (
        f"⏳ *Nueva Solicitud Pendiente*\n\n"
        f"🙋‍♂️ *Solicitante:* {proposal['user']}\n"
        f"📝 *Actividad:* {proposal['desc']}\n"
        f"⏳ *Duración:* {proposal['duration']} horas"
    )

    reply_markup = get_approval_menu(proposal['id'])

    return text, reply_markup

def handle_approval_action(callback_data):
    """
    Handles the owner's approval or rejection of a request.
    """
    action, request_id = callback_data.split(':')

    if action == 'approve':
        # TODO: Update the status of the request to 'approved'
        return f"✅ La solicitud *{request_id}* ha sido aprobada."
    elif action == 'reject':
        # TODO: Update the status of the request to 'rejected'
        return f"❌ La solicitud *{request_id}* ha sido rechazada."

    return "Acción desconocida.", None
