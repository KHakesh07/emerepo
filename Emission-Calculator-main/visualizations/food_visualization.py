import os
import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from streamlit_extras.dataframe_explorer import dataframe_explorer
from streamlit_autorefresh import st_autorefresh
import logging 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR,"..", "..", "data", "emissions.db")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def fetch_food_data(latest_event):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"SELECT dietary_pattern, food_item, emission FROM food_choices WHERE event = ?", (latest_event,))
        data = cursor.fetchall()
        conn.close()
        return data
    except sqlite3.Error as e:
        st.error(f"An error occurred: {e}")
        return []

def get_latest_event():
    """Fetch the latest event name from the Events table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM Events ORDER BY id DESC LIMIT 1")
    event = cursor.fetchone()
    return event[0] if event else None

st_autorefresh(interval=1000, key="latest_evefresh")
latest_event = get_latest_event()

def food_visual():
    latest_event = get_latest_event()
    if st.button("Refresh Data", key="gooa"):
        latest_event = get_latest_event()
        st.success("Data refreshed successfully!")
    data = fetch_food_data(latest_event)

    st.subheader("🍎 Food Emission Data")
    st.write("Event: ", latest_event)

    if data:
        df = pd.DataFrame(data, columns=["Diet", "FoodItem", "Emission (kg CO₂)"])

        # Optional quantity placeholder: if needed, you can add a dummy or estimated 'Quantity' column
        df["Quantity"] = 1  # or derive from somewhere else if you have that data


        st.markdown(f"### 📅 Event: {latest_event}")

        # Descriptive analysis
        total_emission = round(df["Emission (kg CO₂)"].sum(), 3)
        avg_emission = round(df["Emission (kg CO₂)"].mean(), 3)
        max_emission = round(df["Emission (kg CO₂)"].max(), 3)
        min_emission = round(df["Emission (kg CO₂)"].min(), 3)
        no_of_emissions = df["Emission (kg CO₂)"].count()

        # Metrics display
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label='Total Emission (kg CO₂)', value=total_emission)
        with col2:
            st.metric(label='Average Emission (kg CO₂)', value=avg_emission)
        with col3:
            st.metric(label='Highest Recorded Emission (kg CO₂)', value=max_emission)

        col4, col5 = st.columns(2)
        with col4:
            st.metric(label='Lowest Recorded Emission (kg CO₂)', value=min_emission)
        with col5:
            st.metric(label='Number of Emissions Recorded', value=no_of_emissions)

        st.subheader("Quantity of Food items (placeholder)")
        fig = px.scatter(df, x="Quantity", y="FoodItem",  color="Emission (kg CO₂)", color_continuous_scale="Blues", template="plotly_dark", size_max=15)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Emissions")
        cat = st.selectbox("Select option:", ["Pi chart", "Scatter", "Bar plot", "Line Graph"])

        if cat == "Pi chart":
            fig = px.pie(df, names='FoodItem', values="Emission (kg CO₂)", title="Emissions Breakdown", hole=0.3)
            st.plotly_chart(fig, use_container_width=True)

        elif cat == "Scatter":
            fig = px.scatter(df, x="FoodItem", y="Emission (kg CO₂)", title="Emission Distribution", color='Emission (kg CO₂)', color_continuous_scale="Blues", template="plotly_dark", size_max=15)
            st.plotly_chart(fig, use_container_width=True)

        elif cat == "Bar plot":
            fig = px.bar(df, x="FoodItem", y="Emission (kg CO₂)", text="Emission (kg CO₂)", color="Emission (kg CO₂)", color_continuous_scale="blues", title="Emission Distribution")
            fig.update_traces(texttemplate='%{text}', textposition='outside')
            st.plotly_chart(fig, use_container_width=True)

        elif cat == "Line Graph":
            fig = px.line(df, x="Emission (kg CO₂)", y="FoodItem", markers=True, title="Emission Trend by Food Item")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No food emission records found.")
