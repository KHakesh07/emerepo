import sqlite3
import streamlit as st
from modules.sc1_emissions import display_scope1
from visualizations.scope_1Visual import display
import logging
import os
from streamlit_autorefresh import st_autorefresh

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR,"..", "..", "data", "emissions.db")

def get_latest_event():
    """Fetch the latest event name from the Events table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM Events ORDER BY id DESC LIMIT 1")
    event = cursor.fetchone()
    return event[0] if event else None

st_autorefresh(interval=1000, key="latest_event_refresh")
event = get_latest_event()
# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def scope1_page():
    # Check if user is logged in
    if "logged_in_user" not in st.session_state:
        st.error("Please login to access the dashboard.")
        return
    try:
        # Display Scope 1 calculator
        display_scope1(event)

        # Display Scope 1 visualizations
        st.header(" ")
        st.title(" ")
        display()
    except Exception as e:
        st.error(f"An error occurred: {e}")
        logging.error(f"Error in scope1_page: {e}")