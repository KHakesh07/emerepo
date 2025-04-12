import os
import sqlite3
import streamlit as st
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "..", "data")  # Directory for database
DB_PATH = os.path.join(DB_DIR, "emissions.db")  # Full database path

def create_directory(directory: str):
    """Create a directory if it doesn't exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logging.info(f"Created directory: {directory}")

def execute_sql_script(cursor, script_path: str):
    """Execute an SQL script from a file."""
    try:
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"SQL script file not found: {script_path}")

        with open(script_path, 'r') as file:
            sql_script = file.read()

        cursor.executescript(sql_script)
        logging.info(f"Executed SQL script: {script_path}")
    except FileNotFoundError as e:
        st.warning(str(e))
    except sqlite3.Error as e:
        st.error(f"Failed to execute SQL script: {e}")
        logging.error(f"SQL execution error: {e}")

def create_database():
    """Initialize the database and execute the schema script."""
    try:
        # Ensure the data directory exists
        create_directory(DB_DIR)

        # Connect to the database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Execute the SQL script
        sql_script_path = os.path.join(DB_DIR, "emissions.sql")
        execute_sql_script(cursor, sql_script_path)

        # Commit changes and close the connection
        conn.commit()
        logging.info("Database initialized successfully.")
    except sqlite3.Error as e:
        st.error(f"An error occurred while creating the database: {e}")
        logging.error(f"Database initialization failed: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        logging.error(f"Unexpected error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
            logging.info("Database connection closed.")

# Call the function to initialize the database
create_database()
