import os
import streamlit as st
import sqlite3
import logging
from typing import Dict, Tuple

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR,"..", "..", "data", "emissions.db")

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ⚡ Electricity Consumption Emission Factors (kg CO₂ per kWh)
ELECTRICITY_EMISSION_FACTORS = {
    "Lighting and other electrical uses": 1.238,
    "Cooling": 0.709,
    "Nuclear": 0.012,
    "Solar": 0.041,
    "Wind": 0.011,
    "Hydroelectric": 0.024,
}

# ❄ HVAC Refrigerant Emission Factors
HVAC_REFRIGERANTS = {
    "R134a": {"EF (kg CO₂eq/kg)": 1300},
    "R-32": {"EF (kg CO₂eq/kg)": 677},
    "R-410A": {"EF (kg CO₂eq/kg)": 2088},
    "R-290": {"EF (kg CO₂eq/kg)": 3},
    "R-404A": {"EF (kg CO₂eq/kg)": 3922},
    "R-407C": {"EF (kg CO₂eq/kg)": 1774},
    "R-407A": {"EF (kg CO₂eq/kg)": 2107},
    "R-407F": {"EF (kg CO₂eq/kg)": 1824},
    "R-1234yf": {"EF (kg CO₂eq/kg)": 4},
    "R-1234ze(E)": {"EF (kg CO₂eq/kg)": 6},
    "R-600a": {"EF (kg CO₂eq/kg)": 3},
    "R-744": {"EF (kg CO₂eq/kg)": 1},
    "R-123": {"EF (kg CO₂eq/kg)": 77},
    "R-245fa": {"EF (kg CO₂eq/kg)": 1030},
    "R-600": {"EF (kg CO₂eq/kg)": 3},
    "R-32/R-125": {"EF (kg CO₂eq/kg)": 677},
    "R-507A": {"EF (kg CO₂eq/kg)": 3985},
    "R-508B": {"EF (kg CO₂eq/kg)": 13900},
    "R-23": {"EF (kg CO₂eq/kg)": 14800},
    "R-134": {"EF (kg CO₂eq/kg)": 1300},
    "R-717": {"EF (kg CO₂eq/kg)": 1},
}



# 🧮 Calculate Electricity Emissions
def calculate_electricity_emission(category: str, value: float) -> float:
    """Calculate emissions based on electricity consumption."""
    if category in ELECTRICITY_EMISSION_FACTORS:
        return value * ELECTRICITY_EMISSION_FACTORS[category]  # kg CO₂
    return 0  # Default if no match found

# 🧮 Calculate HVAC Emissions
def calculate_hvac_emission(refrigerant: str, mass_leak: float) -> float:
    """Calculate emissions based on HVAC refrigerant leakage."""
    if refrigerant in HVAC_REFRIGERANTS:
        ef = HVAC_REFRIGERANTS[refrigerant]["EF (kg CO₂eq/kg)"]
        return mass_leak * ef  # kg CO₂eq
    return 0

# 📌 Insert Electricity Data into DB
def insert_electricity_data(event: str, category: str, value: float, emission: float):
    """Insert electricity emission data into the database."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO ElectricityEmissions (event, Usage, Value, Emission) VALUES (?, ?, ?, ?)",
                (event, category, value, emission),
            )
            conn.commit()
            logging.info(f"Inserted electricity data for event: {event}")
    except sqlite3.Error as e:
        logging.error(f"Failed to insert electricity data: {e}")
        st.error("An error occurred while saving data. Please try again.")

# 📌 Insert HVAC Data into DB
def insert_hvac_data(event: str, refrigerant: str, mass_leak: float, emission: float):
    """Insert HVAC emission data into the database."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO HVACEmissions (event, Refrigerant, MassLeak, Emission) VALUES (?, ?, ?, ?)",
                (event, refrigerant, mass_leak, emission),
            )
            conn.commit()
            logging.info(f"Inserted HVAC data for event: {event}")
    except sqlite3.Error as e:
        logging.error(f"Failed to insert HVAC data: {e}")
        st.error("An error occurred while saving data. Please try again.")

# 🌱 Suggest Greener Alternatives
def suggest_greener_alternatives(current_refrigerant: str) -> list[Tuple[str, float, float]]:
    """Suggest greener alternatives for a given refrigerant."""
    current_ef = HVAC_REFRIGERANTS[current_refrigerant]["EF (kg CO₂eq/kg)"]
    greener_options = []

    for alt_refrigerant, data in HVAC_REFRIGERANTS.items():
        alt_ef = data["EF (kg CO₂eq/kg)"]
        if alt_ef < current_ef:
            reduction = ((current_ef - alt_ef) / current_ef) * 100
            greener_options.append((alt_refrigerant, alt_ef, reduction))

    return sorted(greener_options, key=lambda x: x[1])  # Sort by EF (ascending)

# ⚡ Show Electricity & HVAC Calculator
def show_electricity_hvac_calculator(event):
    """Display the electricity and HVAC emission calculator."""
    st.subheader("⚡ Electricity & HVAC Emission Calculator")

    # Tabs for Electricity and HVAC
    tab1, tab2 = st.tabs(["Electricity", "HVAC"])



    with tab1:
        # 🔋 Electricity Consumption Section
        st.write("### 🔋 Electricity Consumption")
        category = st.selectbox("Select Energy Use Category", list(ELECTRICITY_EMISSION_FACTORS.keys()))
        value = st.number_input(f"Enter Consumption for {category} (kWh):", min_value=0.0, step=0.1, value=0.0)

        if st.button("Calculate Electricity Emission", key="electricity_calc_button"):
            if value <= 0:
                st.warning("Please enter a valid consumption value.")
            else:
                emission = calculate_electricity_emission(category, value)
                insert_electricity_data(event, category, value, emission)
                st.success(f"Emission from {value} kWh in {category}: {emission:.3f} kg CO₂")

    with tab2:
        # ❄ HVAC Refrigerant Leakage Section
        st.write("### ❄ HVAC Refrigerant Leakage")
        refrigerant = st.selectbox("Select Refrigerant", list(HVAC_REFRIGERANTS.keys()))
        mass_leak = st.number_input(f"Enter Mass Leak for {refrigerant} (kg):", min_value=0.0, step=0.01, value=0.0)

        if st.button("Calculate HVAC Emission", key="hvac_calc_button"):
            if mass_leak <= 0:
                st.warning("Please enter a valid mass leak value.")
            else:
                emission = calculate_hvac_emission(refrigerant, mass_leak)
                insert_hvac_data(event, refrigerant, mass_leak, emission)
                st.success(f"Emission from {mass_leak} kg leakage of {refrigerant}: {emission:.3f} kg CO₂eq")

                # Suggest Greener Alternatives
                st.write("### 🌱 Greener Alternatives")
                greener_options = suggest_greener_alternatives(refrigerant)
                if greener_options:
                    for alt_refrigerant, alt_ef, reduction in greener_options:
                        st.write(
                            f"- **{alt_refrigerant}**: EF = {alt_ef} kg CO₂eq/kg, "
                            f"**Reduction** = {reduction:.2f}%"
                        )
                else:
                    st.info("No greener alternatives available for the selected refrigerant.")