import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from streamlit_extras.dataframe_explorer import dataframe_explorer
import os
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="Emission Analytics Dashboard",
    page_icon="⚡",
    layout="wide"
)



BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR,"..", "..", "data", "emissions.db")

######################### LATEST EVENT ###############################################
def get_latest_event():
    """Fetch the latest event name from the Events table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM Events ORDER BY id DESC LIMIT 1")
    event = cursor.fetchone()
    return event[0] if event else None

event_name = get_latest_event()
st_autorefresh(interval=1000, key="lat_event_refresh")
latest_event = get_latest_event()
st.write(f"Event: {latest_event}")
#######################################################################################

def fetch_data(event, table_name):
    """Fetch data from the database for a specific event name or all events."""
    try:
        conn = sqlite3.connect(DB_PATH)
        query = f"SELECT * FROM {table_name} WHERE event = ?"
        df = pd.read_sql(query, conn, params=(event,))
        conn.close()
        return df
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame()
def display_analytics(df, data_type="Emission"):
    """Display descriptive analytics metrics."""
    total = round(df[data_type].sum(), 3)
    avg = round(df[data_type].mean(), 3)
    max_val = round(df[data_type].max(), 3)
    min_val = round(df[data_type].min(), 3)
    count = df[data_type].count()

    col1, col2, col3 = st.columns(3)
    col1.metric(label=f'Total {data_type}', value=total)
    col2.metric(label=f'Average {data_type}', value=avg)
    col3.metric(label=f'Max {data_type}', value=max_val)

    col4, col5 = st.columns(2)
    col4.metric(label=f'Min {data_type}', value=min_val)
    col5.metric(label='Total Records', value=count)

def plot_graphs(df, event_name, category, value_col):
    """Plot graphs dynamically based on selected event name."""
    title_suffix = f"for {event_name}" if event_name != "All Events" else "for All Events"

    st.subheader(f"Data Distribution {title_suffix}")

    # Area Chart
    st.area_chart(df[[value_col, "Emission"]])

    d1, d2 = st.tabs(["📊 Pie Chart", "📊 Bar Chart"])
    
    # Pie Chart
    with d1:
        fig = px.pie(df, names=category, values="Emission", 
                     title=f"Emissions Breakdown {title_suffix}", hole=0.3)
        st.plotly_chart(fig, use_container_width=True)

    # Bar Chart
    with d2:
        fig = px.bar(df, x=category, y="Emission", 
                     text="Emission", color=value_col, 
                     color_continuous_scale="blues", 
                     title=f"Emission Distribution {title_suffix}")
        fig.update_traces(texttemplate='%{text}', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

def electricity_visual():
    """Display electricity and HVAC emissions visualizations."""
    global event_name
    if st.button("Refresh"):
        event_name = get_latest_event()
        st.rerun()
    tab1, tab2 = st.tabs(["⚡ Electricity Emissions", "❄️ HVAC Emissions"])

    with tab1:
        st.subheader("⚡ Electricity Emission Data")
        df = fetch_data(event_name, "ElectricityEmissions")

        if not df.empty:
            display_analytics(df)

            plot_graphs(df, event_name, "Usage", "Value")
        else:
            st.write("No electricity emission records found.")

    with tab2:
        st.subheader("❄️ HVAC Emission Data")

        df = fetch_data(event_name, "HVACEmissions")

        if not df.empty:

            display_analytics(df)

            plot_graphs(df, event_name, "Refrigerant", "MassLeak")
        else:
            st.write("No HVAC emission records found.")










