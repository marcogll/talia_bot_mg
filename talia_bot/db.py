# talia_bot/db.py
# This module will handle the database connection and operations.

import sqlite3
import logging

DATABASE_FILE = "talia_bot/data/users.db"

logger = logging.getLogger(__name__)

def get_db_connection():
    """Creates a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def setup_database():
    """Sets up the database tables if they don't exist."""
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

        # Create the conversations table for the flow engine
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                user_id INTEGER PRIMARY KEY,
                flow_id TEXT NOT NULL,
                current_step_id INTEGER NOT NULL,
                collected_data TEXT
            )
        """)

        conn.commit()
        logger.info("Database setup complete. 'users' and 'conversations' tables are ready.")
    except sqlite3.Error as e:
        logger.error(f"Database error during setup: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    # This allows us to run the script directly to initialize the database
    logging.basicConfig(level=logging.INFO)
    logger.info("Running database setup manually...")
    setup_database()
    logger.info("Manual setup finished.")
