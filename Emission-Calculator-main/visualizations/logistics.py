import logging
import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import os
from streamlit_autorefresh import st_autorefresh
import logging
# Database setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR,"..", "..", "data", "emissions.db")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def fetch_event_data():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM Events ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        conn.close()

        # fetchone returns a tuple like ('EventName',), so extract the value
        return result[0] if result else None
    except Exception as e:
        st.error(f"Database Error: {e}")
        return None
    
st_autorefresh(interval=1000, key="lates_event_refresh")
event = fetch_event_data()

def fetch_logistics_data(event):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            query = """
                SELECT * 
                FROM logistics_emissions 
                WHERE Event = ? 
                ORDER BY created_at DESC
            """
            df = pd.read_sql_query(query, conn, params=(event,))
        return df
    except Exception as e:
        st.error(f"Database Error: {e}")
        return pd.DataFrame()

def logist_vis():
    c1, c2 = st.columns(2)
    with c1:
        st.title("🚛 Logistics Emissions Dashboard")
        st.markdown("Analyze emissions data stored in the `logistics_emissions` table.")
    with c2:
        event = fetch_event_data()
        if st.button("Refresh Data", on_click=fetch_logistics_data, args=(event,)):
            event = fetch_event_data()
            st.rerun()
            st.success("Data refreshed successfully!")

    df = fetch_logistics_data(event)

    if df.empty:
        st.warning("No data available in the logistics_emissions table.")
        return

    # Metrics
    st.subheader("📊 Summary Statistics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Records", len(df))
    col2.metric("Total Distance (km)", round(df["distance_km"].sum(), 2))
    col3.metric("Total Emissions (kg CO₂)", round(df["total_emission"].sum(), 2))

    col4, col5 = st.columns(2)
    col4.metric("Avg Emission/Trip (kg)", round(df["total_emission"].mean(), 2))
    col5.metric("Avg Distance/Trip (km)", round(df["distance_km"].mean(), 2))

    # Visualizations
    st.subheader("📦 Emissions by Transport Mode")
    fig = px.bar(df.groupby("transport_mode")["total_emission"].sum().reset_index(),
                 x="transport_mode", y="total_emission",
                 title="Total Emissions per Transport Mode",
                 text_auto='.2s', color="transport_mode")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📍 Emission Distribution by Route")
    fig2 = px.scatter(df, x="origin", y="destination", size="total_emission",
                      color="transport_mode", hover_name="material",
                      title="Emission Bubbles by Route and Mode",
                      labels={"total_emission": "CO₂ Emission (kg)"})
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("📅 Emissions Over Time")
    df['created_at'] = pd.to_datetime(df['created_at'])
    df_by_date = df.groupby(df['created_at'].dt.date)['total_emission'].sum().reset_index()
    fig3 = px.line(df_by_date, x="created_at", y="total_emission", markers=True, title="Emissions Over Time")
    st.plotly_chart(fig3, use_container_width=True)

# Run it as a standalone page
if __name__ == "__main__":
    logist_vis()
