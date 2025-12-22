# bot/db.py
# This module will handle the database connection and operations.

import sqlite3
import logging
import os
import threading

DATABASE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "users.db")

logger = logging.getLogger(__name__)

# Use a thread-local object to manage the database connection
local = threading.local()

def get_db_connection():
    """Creates a connection to the SQLite database."""
    if hasattr(local, "conn"):
        try:
            # Check if connection is open
            local.conn.execute("SELECT 1")
            logger.debug("Reusing existing database connection")
            return local.conn
        except sqlite3.ProgrammingError:
            logger.warning("Detected closed connection in thread-local storage. Recreating.")
            del local.conn
    
    logger.debug("Creating new database connection")
    local.conn = sqlite3.connect(DATABASE_FILE, check_same_thread=False)
    local.conn.row_factory = sqlite3.Row
    return local.conn

def close_db_connection():
    """Closes the database connection."""
    if hasattr(local, "conn"):
        logger.debug("Closing database connection")
        try:
            local.conn.close()
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")
        finally:
            if hasattr(local, "conn"):
                del local.conn

def setup_database():
    """Sets up the database tables if they don't exist."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Create the users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'crew', 'client')),
                name TEXT,
                employee_id TEXT,
                branch TEXT
            )
        """)

        # Create the conversations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                user_id INTEGER PRIMARY KEY,
                flow_id TEXT NOT NULL,
                current_step_id INTEGER NOT NULL,
                collected_data TEXT
            )
        """)

        conn.commit()
        logger.info("Database setup complete. 'users' table is ready.")
    except sqlite3.Error as e:
        logger.error(f"Database error during setup: {e}")
    finally:
        if conn:
            close_db_connection()

if __name__ == '__main__':
    # This allows us to run the script directly to initialize the database
    logging.basicConfig(level=logging.INFO)
    logger.info("Running database setup manually...")
    setup_database()
    logger.info("Manual setup finished.")
