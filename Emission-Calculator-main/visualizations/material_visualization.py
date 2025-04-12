import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import logging
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR,"..", "..", "data", "emissions.db")
# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

######################### LATEST EVENT ###############################################
def get_latest_event():
    """Fetch the latest event name from the Events table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM Events ORDER BY id DESC LIMIT 1")
    event = cursor.fetchone()
    return event[0] if event else None
#######################################################################################

def fetch_material_data(category, event):
    """Fetch material emissions data from the database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, event, Weight, Quantity, Emission, Timestamp FROM Materials WHERE Category = ? AND event=?", (category, event,))
        data = cursor.fetchall()
        conn.close()
        return data
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        logging.error(f"Error fetching material data: {e}")
        return []

def display_descriptive_analytics(df):
    """Display descriptive analytics for material emissions."""
    total_emission = round(df["Emission"].sum(), 3)
    avg_emission = round(df["Emission"].mean(), 3)
    max_emission = round(df["Emission"].max(), 3)
    min_emission = round(df["Emission"].min(), 3)
    day_with_highest_emission = df["Timestamp"].max()
    no_of_emissions = df["Emission"].count()

    st.subheader("Descriptive Analysis")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label='Total Emission (kg CO₂)', value=total_emission, delta_color="off")
    with col2:
        st.metric(label='Average Emission (kg CO₂)', value=avg_emission, delta_color="off")
    with col3:
        st.metric(label='Highest Recorded Emission (kg CO₂)', value=max_emission, delta_color="off")

    col4, col5, col6 = st.columns(3)
    with col4:
        st.metric(label='Lowest Recorded Emission (kg CO₂)', value=min_emission, delta_color="off")
    with col5:
        st.metric(label='Number of Emissions Recorded', value=no_of_emissions, delta_color="off")
    with col6:
        st.metric(label='Day with Highest Emission', value=day_with_highest_emission, delta_color="off")

def visualize(category, event_name):
    """Display material emissions visualizations."""
    event_name = get_latest_event()
    data = fetch_material_data(category, event_name)
    if not data:
        st.write("No records found.")
        return

    df = pd.DataFrame(data, columns=["id", "event", "Weight", "Quantity", "Emission", "Timestamp"])
    df["Weight"] = df["Weight"].astype(float)
    df["Quantity"] = df["Quantity"].astype(float)
    df["Emission"] = df["Emission"].astype(float)

    # Scatter Plot: Total Emission by Events
    st.subheader("Total Emission by Events")
    fig = px.scatter(df, x="Timestamp", y="Emission", size="Quantity", color="Emission",
                     title="Total Emission by Events", color_continuous_scale="Blues")
    fig.update_traces(marker=dict(opacity=0.8, line=dict(width=1, color="black")))
    st.plotly_chart(fig, use_container_width=True)

    # Descriptive Analytics
    display_descriptive_analytics(df)

    # Emissions Visualization
    st.subheader("Emissions Visualization")
    chart_type = st.selectbox("Select Chart Type:", ["Scatter", "Bar Plot"])

    if chart_type == "Scatter":
        fig = px.scatter(df, x="Weight", y="Emission", size="Quantity", color="Emission",
                         title="Weight vs CO₂ Emission", color_continuous_scale="Blues")
        fig.update_traces(marker=dict(opacity=0.8, line=dict(width=1, color="black")))
        st.plotly_chart(fig, use_container_width=True)
    elif chart_type == "Bar Plot":
        fig = px.bar(df, x="Quantity", y="Emission", text="Emission", color="Emission",
                     color_continuous_scale="Blues", title="Quantity vs CO₂ Emission")
        fig.update_traces(texttemplate='%{text}', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)