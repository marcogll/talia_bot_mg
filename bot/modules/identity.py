# bot/modules/identity.py
# Este script maneja los roles y permisos de los usuarios.

import logging
from bot.db import get_db_connection
from bot.config import ADMIN_ID

logger = logging.getLogger(__name__)

def add_user(telegram_id, role, name=None, employee_id=None, branch=None):
    """
    Añade un nuevo usuario o actualiza el rol de uno existente.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (telegram_id, role, name, employee_id, branch)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(telegram_id) DO UPDATE SET
            role = excluded.role,
            name = excluded.name,
            employee_id = excluded.employee_id,
            branch = excluded.branch
        """, (telegram_id, role, name, employee_id, branch))
        conn.commit()
        logger.info(f"Usuario {telegram_id} añadido/actualizado con el rol {role}.")
        return True
    except Exception as e:
        logger.error(f"Error al añadir/actualizar usuario {telegram_id}: {e}")
        return False
    finally:
        if conn:
            conn.close()

def get_user_role(telegram_id):
    """
    Determina el rol de un usuario.
    Roles: 'admin', 'crew', 'client'.
    """
    # El admin principal se define en el .env para el primer arranque
    # Se convierten ambos a int para una comparación segura de tipos.
    try:
        if int(telegram_id) == int(ADMIN_ID):
            return 'admin'
    except (ValueError, TypeError):
        logger.warning("ADMIN_ID no es un número válido. Ignorando la comparación.")
        pass

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE telegram_id = ?", (telegram_id,))
        user = cursor.fetchone()

        if user:
            logger.debug(f"Rol encontrado para {telegram_id}: {user['role']}")
            return user['role']
        else:
            # Si no está en la DB, es un cliente nuevo
            logger.debug(f"No se encontró rol para {telegram_id}, asignando 'client'.")
            return 'client'
    except Exception as e:
        logger.error(f"Error al obtener el rol para {telegram_id}: {e}")
        return 'client' # Fallback seguro
    finally:
        if conn:
            conn.close()

def is_admin(telegram_id):
    """Verifica si un usuario es administrador."""
    return get_user_role(telegram_id) == 'admin'

def is_crew(telegram_id):
    """Verifica si un usuario es del equipo (crew) o administrador."""
    return get_user_role(telegram_id) in ['admin', 'crew']
