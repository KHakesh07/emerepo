import os
import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import logging
from streamlit_autorefresh import st_autorefresh

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR,"..", "..", "data", "emissions.db")

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

############################## EVENT ##################################################
def get_latest_event():
    """Fetch the latest event name from the Events table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM Events ORDER BY id DESC LIMIT 1")
    event = cursor.fetchone()
    return event[0] if event else None

st_autorefresh(interval=1000, key="latest_event_refresh")
event_name = get_latest_event()

######################################################################################


def fetch_transport_data(event_name):
    """Fetch transport emissions data from the database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT mode, type, origin, destination, distance, Emission FROM transport_data WHERE event = ?", (event_name,))
        data = cursor.fetchall()
        conn.close()
        return data
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        logging.error(f"Error fetching transport data: {e}")
        return []




def display_descriptive_analytics(df):
    """Display descriptive analytics for transport emissions."""
    total_emission = round(df["Emission (kg CO₂)"].sum(), 3)
    avg_emission = round(df["Emission (kg CO₂)"].mean(), 3)
    max_emission = round(df["Emission (kg CO₂)"].max(), 3)
    min_emission = round(df["Emission (kg CO₂)"].min(), 3)
    no_of_emissions = df["Emission (kg CO₂)"].count()

    st.subheader("Descriptive Analysis")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label='Total Emission (kg CO₂)', value=total_emission, delta_color="off")
    with col2:
        st.metric(label='Average Emission (kg CO₂)', value=avg_emission, delta_color="off")
    with col3:
        st.metric(label='Highest Recorded Emission (kg CO₂)', value=max_emission, delta_color="off")

    col4, col5 = st.columns(2)
    with col4:
        st.metric(label='Lowest Recorded Emission (kg CO₂)', value=min_emission, delta_color="off")
    with col5:
        st.metric(label='Number of Emissions Recorded', value=no_of_emissions, delta_color="off")
    st.write("")
    st.write("")
    st.write("")

def transport_visual():
    """Display transport emissions visualizations."""
    st.subheader("🚗 Transport Emission Data")
    event_name = get_latest_event()
    if st.button("Refresh"):
        event_name = get_latest_event()
        st.rerun()
    st.write("Event: ", event_name)

    # Fetch data (cached)
    data = fetch_transport_data(event_name)
    if not data:
        st.warning("No transport emission records found.")
        return

    # Convert data to DataFrame
    df = pd.DataFrame(data, columns=["Mode", "Type", "Origin", "Destination", "Distance (km)", "Emission (kg CO₂)"])
  
    # Descriptive analytics
    display_descriptive_analytics(df)
    column = st.selectbox("Select the column for analysis:", ["Distance (km)", "Emission (kg CO₂)"])


    cols = st.columns(2)
    with cols[0]:
        st.subheader("Custom Visualization")
        fig1 = px.bar(df, x="Mode", y=column, title=f"{column} Bar Chart", height=400, width=400)
        st.plotly_chart(fig1, use_container_width=True)
    with cols[1]:
        st.subheader("Emission Comparison by Transport Mode")
        fig2 = px.bar(df, x="Type", y=column, color="Mode", text="Emission (kg CO₂)", height=400, width=400)
        st.plotly_chart(fig2, use_container_width=True)
    

# Example usage
if __name__ == "__main__":
    transport_visual()
