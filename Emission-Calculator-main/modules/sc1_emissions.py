import streamlit as st
import sqlite3
import json
import logging
from typing import List, Dict
import os
import plotly.express as px  # Added for pie chart

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "..", "data", "emissions.db")

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Emission factors dictionary
EMISSION_FACTORS = {
    "Diesel": 0.2496,
    "Coal": 0.3230,
    "Petroleum Gas (LPG)": 0.2106,
    "Electricity": 0.82,
}

# 🧮 Calculate Emission
def calculate_emission(fuel_type: str, consumption: float) -> float:
    return consumption * EMISSION_FACTORS.get(fuel_type, 0)

# 📌 Insert Scope 1 Data into DB
def insert_scope1_data(event: str, fuels: List[str], consumptions: List[float], emissions: List[float], total_emission: float):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            fuels_json = json.dumps(fuels)
            consumptions_json = json.dumps(consumptions)
            emissions_json = json.dumps(emissions)

            c.execute("""
                INSERT INTO Scope1 (event, fuels, consumptions, emissions, total_emission)
                VALUES (?, ?, ?, ?, ?)""",
                (event, fuels_json, consumptions_json, emissions_json, total_emission)
            )
            conn.commit()
            st.success("Emission data saved successfully!")
            logging.info(f"Inserted Scope 1 data for event: {event}")
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        logging.error(f"Failed to insert Scope 1 data: {e}")

# 🏭 Display Scope 1 Calculator
def display_scope1(event):
    st.title("Scope 1 Emissions Calculator")
    st.write("Scope 1 emissions refer to direct greenhouse gas (GHG) emissions from sources that are owned or controlled by an organization.")
    
    if "fuel_entries" not in st.session_state:
        st.session_state.fuel_entries = [{"id": 0, "fuel_type": "Diesel", "consumption": 0.0}]

    total_emission = 0
    fuels, consumptions, emissions = [], [], []

    for entry in st.session_state.fuel_entries:
        index = entry["id"]
        cols = st.columns([3, 3, 2])

        with cols[0]:
            fuel_type = st.selectbox(
                f"Fuel Type {index + 1}:", EMISSION_FACTORS.keys(),
                key=f"fuel_{index}", index=list(EMISSION_FACTORS.keys()).index(entry["fuel_type"])
            )

        unit = {
            "Diesel": "litres",
            "Coal": "kg",
            "Petroleum Gas (LPG)": "kg",
            "Electricity": "kWh"
        }.get(fuel_type, "units")

        with cols[1]:
            consumption = st.number_input(
                f"Consumption {index + 1} ({unit}):",
                min_value=0.0, step=0.1, value=entry["consumption"],
                key=f"consumption_{index}"
            )

        with cols[2]:
            if st.button("Remove", key=f"remove_{index}"):
                st.session_state.fuel_entries = [e for e in st.session_state.fuel_entries if e["id"] != index]
                st.rerun()

        emission = calculate_emission(fuel_type, consumption)
        total_emission += emission
        fuels.append(fuel_type)
        consumptions.append(consumption)
        emissions.append(emission)

    st.subheader(f"Total Emission: {total_emission:.3f} kg CO₂")

    # 🥧 Pie Chart for Emissions by Fuel
    if emissions and sum(emissions) > 0:
        pie_data = {"Fuel Type": fuels, "Emission (kg CO₂)": emissions}
        fig = px.pie(pie_data, names="Fuel Type", values="Emission (kg CO₂)",
                     title="Emission Contribution by Fuel Type")
        st.plotly_chart(fig)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save Emission Data"):
            if not event:
                st.warning("Event name is not set. Please go to the Overview page and save an event first.")
            else:
                insert_scope1_data(event, fuels, consumptions, emissions, total_emission)
    with col2:
        if st.button("Add Another Fuel"):
            new_id = max([e["id"] for e in st.session_state.fuel_entries], default=-1) + 1
            st.session_state.fuel_entries.append({"id": new_id, "fuel_type": "Diesel", "consumption": 0.0})
            st.rerun()
