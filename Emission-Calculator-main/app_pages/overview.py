import sqlite3
import streamlit as st
from app_pages.scope1 import scope1_page
from app_pages.scope2 import scope2_page
from app_pages.scope3 import scope3_page
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

st_autorefresh(interval=1000, key="latent_refres")
event_name = get_latest_event()


def overview_page():
    # Check if user is logged in
    if "logged_in_user" not in st.session_state:
        st.error("Login is required")
        return

    # Add links to other pages
    st.markdown("---")
    st.subheader("Explore Calculator")

    event_name =  st.text_input("Enter event name",key="event_name")
    if st.button("Save"):
        with sqlite3.connect(DB_PATH) as conn:
                c = conn.cursor()
                c.execute("INSERT INTO Events (name) VALUES (?)",(event_name,))
                conn.commit()   
        st.success(f"Event {event_name} saved successfully")

    # Define page names
    overview = "Overview"
    scope1 = "Scope 1"
    scope2 = "Scope 2"
    scope3 = "Scope 3"

    # Initialize session state
    if "current_page" not in st.session_state:
        st.session_state.current_page = overview  # Default to Overview page
    event_name = get_latest_event()
    cola, colb = st.columns(2)
    with cola:
        a, b =st.columns(2)
        with a:
            st.subheader("Event Name:")
        with b:
            st.subheader(event_name)
    with colb:
        if st.button("Refresh Data", key="refresnt"):
            event_name = get_latest_event()
            st.success("Data refreshed successfully!")
    # Navigation buttons
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Scope 1 Calculator"):
            st.session_state.current_page = scope1
            st.rerun()

    with col2:
        if st.button("Scope 2 Calculator"):
            st.session_state.current_page = scope2
            st.rerun()

    with col3:
        if st.button("Scope 3 Calculator"):
            st.session_state.current_page = scope3
            st.rerun()

    # Display the selected page
    st.markdown("---")  # Divider for clarity

    if st.session_state.current_page == overview:
        return
    elif st.session_state.current_page == scope1:
        scope1_page()
    elif st.session_state.current_page == scope2:
        scope2_page()
    elif st.session_state.current_page == scope3:
        scope3_page()
