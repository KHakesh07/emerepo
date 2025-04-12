import ast
import json
import os
import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import plotly.graph_objects as go
import logging
from streamlit_autorefresh import st_autorefresh
from plotly.subplots import make_subplots
from visualizations.report import report

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR,"..", "..", "data", "emissions.db")

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        background-color: #343E49;
    }
    .stApp {
        background-color: #343E49;
    }
    .metric-card {
        background-color: white;
        color: black;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        margin-bottom: 20px;
    }
    .metric-card.primary {
        background-color: #10485E;
        color: white;
    }
    .metric-card h3 {
        margin-bottom: 5px;
        font-size: 1.2rem;
    }
    .metric-card h2 {
        font-size: 1.8rem;
        margin: 0;
    }
    .section-title {
        font-size: 1.3rem;
        margin-bottom: 15px;
        padding-bottom: 5px;
        border-bottom: 1px solid #ddd;
    }
    .chart-container {
        background-color: #3A4655;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

######################## - GET THE LATEST EVENT DETAILS - #############################
def get_latest_event():
    """Fetch the latest event name from the Events table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM Events ORDER BY id DESC LIMIT 1")
    event = cursor.fetchone()
    return event[0] if event else None

st_autorefresh(interval=1000, key="latest_event_refres")
event_name = get_latest_event()


##############################################################################################

def fetch_emissions_data(event_name):
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT * FROM EmissionsSummary WHERE Event = ?"
    df = pd.read_sql_query(query, conn, params=(event_name,))
    conn.close()
    return df
## Calculate totals by scope
def calculate_scope_totals(df):
    scope_totals = df.groupby('Category')['Emission'].sum().to_dict()
    return scope_totals



def get_emission_journey(event_name):
    conn = sqlite3.connect(DB_PATH)

    scope_map = {
        "HVACEmissions": "Scope 1",
        "Scope1": "Scope 1",
        "ElectricityEmissions": "Scope 2",
        "transport_data": "Scope 3",
        "Materials": "Scope 3",
        "logistics_emissions": "Scope 3",
        "food_choices": "Scope 3"
    }

    query = f"""
    SELECT SourceTable, Emission, Timestamp FROM (
        SELECT 'HVACEmissions' AS SourceTable, Emission, Timestamp FROM HVACEmissions WHERE event = ?
        UNION ALL
        SELECT 'Scope1', total_emission AS Emission, Timestamp FROM Scope1 WHERE event = ?
        UNION ALL
        SELECT 'ElectricityEmissions', Emission, Timestamp FROM ElectricityEmissions WHERE event = ?
        UNION ALL
        SELECT 'transport_data', Emission, NULL AS Timestamp FROM transport_data WHERE event = ?
        UNION ALL
        SELECT 'Materials', Emission, Timestamp FROM Materials WHERE event = ?
        UNION ALL
        SELECT 'logistics_emissions', total_emission AS Emission, created_at AS Timestamp FROM logistics_emissions WHERE Event = ?
        UNION ALL
        SELECT 'food_choices', emission AS Emission, NULL FROM food_choices WHERE event = ?
    )
    """
    df = pd.read_sql_query(query, conn, params=[event_name]*7)
    conn.close()

    df["Timestamp"] = pd.to_datetime(df["Timestamp"]).fillna(method="ffill")
    df["Scope"] = df["SourceTable"].map(scope_map)
    df = df.sort_values("Timestamp")

    return df

def visual2_what_if_simulation():
    st.subheader("🔮 What-If Scenario Simulator")

    # Real emission data
    df = fetch_emissions_data(event_name)
    actual_total = df["Emission"].sum()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Simulate alternative greener choices and see potential CO₂ savings!**")
        st.markdown("""
<style>
/* General blue color customization */
input[type=range] {
    accent-color: #1E90FF;  /* Blue (DodgerBlue) */
}

/* Webkit browsers (Chrome, Safari) */
input[type=range]::-webkit-slider-thumb {
    background: #1E90FF;
}
input[type=range]::-webkit-slider-runnable-track {
    background: #87CEFA;
}

/* Firefox */
input[type=range]::-moz-range-thumb {
    background: #1E90FF;
}
input[type=range]::-moz-range-track {
    background: #87CEFA;
}
</style>
""", unsafe_allow_html=True)


    # Simulate values
        logistics_slider = st.slider("🌍 % Reduction in Logistics Emissions", 0, 100, 0)
        food_slider = st.slider("🥗 % Shift to Sustainable Food Choices", 0, 100, 0)
        electricity_slider = st.slider("⚡ % Optimization in Electricity Usage", 0, 100, 0)

    # Calculate potential savings
        logistics = df[df['SourceTable'] == 'logistics_emissions']["Emission"].sum()
        food = df[df['SourceTable'] == 'food_choices']["Emission"].sum()
        electricity = df[df['SourceTable'] == 'ElectricityEmissions']["Emission"].sum()

        savings = (
            logistics * (logistics_slider / 100.0) +
            food * (food_slider / 100.0) +
            electricity * (electricity_slider / 100.0)
        )

        new_total = actual_total - savings

        st.metric(label="🎯 Original Emissions", value=f"{actual_total:.2f} tCO₂e")
        st.metric(label="🌱 Projected Emissions (If Actions Taken)", value=f"{new_total:.2f} tCO₂e")
        st.metric(label="💚 Potential CO₂ Saved", value=f"{savings:.2f} tCO₂e")
    with col2:
        fig = go.Figure()
        fig.add_trace(go.Indicator(
            mode="gauge+number+delta",
            value=new_total,
            delta={'reference': actual_total},
            title={'text': "Projected Emissions"},
            gauge={'axis': {'range': [0, max(actual_total, new_total) + 10]},
               'bar': {'color': "green"},
               'steps': [
                   {'range': [0, actual_total], 'color': "#87CEEB"},
                   {'range': [actual_total, max(actual_total, new_total)+10], 'color': "lightgray"}
               ]}
        ))
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig, use_container_width=True)


# Main dashboard function
def vis():
    # Fetch and prepare data
    event_name = get_latest_event()
    df = fetch_emissions_data(event_name)
    st.title("Emissions Dashboard")
    st.markdown(f"### Track Your {event_name} Carbon Footprintss")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Total Emissions")
        st.metric(label="Total Emissions", value=f"{df['Emission'].sum():.2f} tCO₂e")
    with col2:
        if st.button("Refresh Data", on_click=fetch_emissions_data, args=(event_name,)):
            event_name = get_latest_event()
            st.rerun()
            st.success("Data refreshed successfully!")
    
    # Charts section
    st.markdown("---")
    st.markdown("### Emissions Analysis - Activities")
    
    col4, col5 = st.columns(2)
    
    with col4:
        # Pie chart for emission distribution
        fig_pie = px.pie(
            df.groupby('Category')['Emission'].sum().reset_index(),
            values='Emission',
            names='Category',
            title=f"Emissions Distribution by Category in Event {event_name}",
            color_discrete_sequence=['#1E90FF', '#4682B4', '#87CEEB']
        )
        fig_pie.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            title_font_color='#E8EBFF'
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col5:
        # Bar chart for sources
        top_sources = (df.groupby('SourceTable')['Emission'].sum().reset_index().sort_values(by='Emission', ascending=True).head(5))
        fig_bar = px.bar(
            top_sources.groupby(['SourceTable'])['Emission'].sum().reset_index(),
            x='SourceTable',
            y='Emission',
            
            title=f"Top Highest Emissions Recorded In this Event {event_name}", 
            color='SourceTable',
            text='Emission',
            color_discrete_sequence=['#20B2AA', '#4169E1', '#00CED1', '#1E90FF', '#87CEFA', '#4682B4']
        )
        fig_bar.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            title_font_color='#E8EBFF',
            showlegend=False
        )
        fig_bar.update_traces(
            texttemplate='%{text:.2s}',  # Show short form (e.g., 2.1k)
            textposition='auto'          # 🟢 Place text on the bar
        )
        st.plotly_chart(fig_bar, use_container_width=True)



    st.markdown("---")
    visual2_what_if_simulation()
    st.markdown("---")
    report()



# Run the dashboard
if __name__ == "__main__":
    vis()