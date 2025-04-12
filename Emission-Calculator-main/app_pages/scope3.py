import streamlit as st
from modules.material import show_material_calculator
from visualizations.material_visualization import visualize
from visualizations.transportation_visualization import transport_visual
from visualizations.food_visualization import food_visual
from visualizations.logistics import logist_vis
from modules.logistics import logist_calculator
import sqlite3
import pandas as pd
import plotly.express as px
from streamlit_extras.dataframe_explorer import dataframe_explorer
import logging
import os
from streamlit_autorefresh import st_autorefresh

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR,"..", "..", "data", "emissions.db")

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_latest_event():
    """Fetch the latest event name from the Events table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM Events ORDER BY id DESC LIMIT 1")
    event = cursor.fetchone()
    return event[0] if event else None

st_autorefresh(interval=10, limit=100, key="dataframe_explorer")
event = get_latest_event()

def scope3_page():
    
    event = get_latest_event()
    # Check if user is logged in
    if "logged_in_user" not in st.session_state:
        st.error("Please login first!")
        return

    # Calculations Section: Tabs for each calculator
    st.subheader("Scope 3 Emission Calculator")
    calc_tab1, calc_tab2 = st.tabs([
        "Materials Calculator", "Logistics Calculator"
    ])

    with calc_tab1:
        show_material_calculator(event)

    with calc_tab2:
        logist_calculator()
    st.title(" ")
    # Emission Analysis Section: Tabs for visualizations
    st.header("Emission Analysis")
    vis_tab1, vis_tab2, vis_tab3, vis_tab4 = st.tabs([
        "Transportation", "Logistics", "Materials", "Foods and Vegetables"
    ])

    with vis_tab1:
        try:
            transport_visual()
        except Exception as e:
            st.error(f"An error occurred while loading transportation visualizations: {e}")
            logging.error(f"Error in transportation visualization: {e}")

    with vis_tab2:
        try:
            logist_vis()
        except Exception as e:
            st.error(f"An error occurred while loading logistics visualizations: {e}")
            logging.error(f"Error in logistics visualization: {e}")

    with vis_tab3:
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT * FROM Materials WHERE event=?", (event,))
            data1 = cur.fetchall()
            conn.close()
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Data:")
            with col2: 
                event_name = get_latest_event()
                if st.button("Refresh", key="Go"):
                    event_name = get_latest_event()
                    st.rerun

            category = st.selectbox("Select a category", ["Trophies", "Banners", "Momentoes", "Kit"], key="Hake")
            visualize(category, event)
        except Exception as e:
            st.error(f"An error occurred while loading materials data: {e}")
            logging.error(f"Error in materials visualization: {e}")

    with vis_tab4:
        try:
            food_visual()
        except Exception as e:
            st.error(f"An error occurred while loading food visualizations: {e}")
            logging.error(f"Error in food visualization: {e}")
