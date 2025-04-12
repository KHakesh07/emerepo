import os
import streamlit as st
import sqlite3
import logging
from typing import Dict, Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR,"..", "..", "data", "emissions.db")

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# 🏆 Emission Factors (kg CO₂ per kg)
EMISSION_FACTORS = {
    "Trophies": {"metal": 2.54, "plastic": 1.32},
    "Banners": {"banner": 7.342},
    "Momentoes": {"metal": 4.98, "plastic": 0.425},
    "Kit": {"recycled_paper": 1.58, "seed_papers": 0.005, "pen": 2.28, "plant": 0},
}

# 📌 Insert Data into DB
def insert_material_data(event: str, category: str, weight: float, quantity: int, emission: float):
    """Insert material emission data into the database."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO Materials (event, Category, Weight, Quantity, Emission) VALUES (?, ?, ?, ?, ?)",
                (event, category, weight, quantity, emission),
            )
            conn.commit()
            st.success("Material emission data saved successfully!")
            logging.info(f"Inserted material data for {category} ({event})")
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        logging.error(f"Failed to insert material data: {e}")

# 🧮 Calculate Emission for Trophies
def calculate_trophy_emission(weight: float, quantity: int) -> float:
    """Calculate emissions for trophies."""
    metal_emission = (3 / 5) * weight * EMISSION_FACTORS["Trophies"]["metal"]
    plastic_emission = (2 / 5) * weight * EMISSION_FACTORS["Trophies"]["plastic"]
    return (metal_emission + plastic_emission) * quantity

# 🧮 Calculate Emission for Banners
def calculate_banner_emission(weight: float, quantity: int) -> float:
    """Calculate emissions for banners."""
    return weight * EMISSION_FACTORS["Banners"]["banner"] * quantity

# 🧮 Calculate Emission for Momentoes
def calculate_momento_emission(weight: float, quantity: int) -> float:
    """Calculate emissions for momentoes."""
    metal_emission = (3 / 5) * weight * EMISSION_FACTORS["Momentoes"]["metal"]
    plastic_emission = (2 / 5) * weight * EMISSION_FACTORS["Momentoes"]["plastic"]
    return (metal_emission + plastic_emission) * quantity

# 🧮 Calculate Emission for Kit
def calculate_kit_emission(weight: float, quantity: int) -> float:
    """Calculate emissions for kits."""
    return (EMISSION_FACTORS["Kit"]["recycled_paper"] + EMISSION_FACTORS["Kit"]["seed_papers"] + EMISSION_FACTORS["Kit"]["pen"] + EMISSION_FACTORS["Kit"]["plant"]) * weight * quantity

# 🧮 Calculate Emission for Individual Kit Items
def calculate_kit_item_emission(category: str, weight: float, quantity: int) -> float:
    """Calculate emissions for individual kit items."""
    if category in EMISSION_FACTORS["Kit"]:
        return weight * EMISSION_FACTORS["Kit"][category] * quantity
    return 0

# 🏆 Show Material Calculator
def show_material_calculator(event):
    """Display the material emission calculator."""
    st.subheader("🏆 Material Emission Calculator")


    category = st.selectbox("Select a category", ["Trophies", "Banners", "Momentoes", "Kit"])

    if category == "Trophies":
        weight = st.number_input("Enter trophy weight (kg):", min_value=0.1, step=0.1, value=1.0)
        quantity = st.number_input(f"For How many {category} do you want to find emission?", min_value=1, step=1, value=1)
        if st.button("Calculate & Save"):
            emission = calculate_trophy_emission(weight, quantity)
            insert_material_data(event, category, weight, quantity, emission)
            st.success(f"Emission for {weight} kg trophy: {emission:.3f} kg CO₂")

    elif category == "Banners":
        weight = st.number_input("Enter weight of banner (kg):", min_value=0.1, step=0.1, value=1.0)
        quantity = st.number_input(f"For How many {category} do you want to find emission?", min_value=1, step=1, value=1)
        if st.button("Calculate & Save"):
            emission = calculate_banner_emission(weight, quantity)
            insert_material_data(event, category, weight, quantity, emission)
            st.success(f"Emission for {weight} kg banner: {emission:.3f} kg CO₂")

    elif category == "Momentoes":
        weight = st.number_input("Enter weight of momento (kg):", min_value=0.1, step=0.1, value=1.0)
        quantity = st.number_input(f"For How many {category} do you want to find emission?", min_value=1, step=1, value=1)
        if st.button("Calculate & Save"):
            emission = calculate_momento_emission(weight, quantity)
            insert_material_data(event, category, weight, quantity, emission)
            st.success(f"Emission for {weight} kg momento: {emission:.3f} kg CO₂")

    elif category == "Kit":
        st.write("Kit is a combination of Recycled paper kit, seed papers, pen, and plant for felicitation.")
        tab1, tab2 = st.tabs(["Calculate for Full kit", "Calculate for Individual items in kit"])

        with tab1:
            weight = st.number_input("Enter weight of kit (kg):", min_value=0.1, step=0.1, value=1.0)
            quantity = st.number_input("Enter Quantity of kit:", min_value=1, step=1, value=1)
            if st.button("Calculate & Save", key="kit"):
                emission = calculate_kit_emission(weight, quantity)
                insert_material_data(event, category, weight, quantity, emission)
                st.success(f"Emission for {quantity} kit: {emission:.3f} kg CO₂")

        with tab2:
            item_category = st.selectbox("Select a category", ["Recycled paper kit", "Seed papers", "Pen"])
            weight = st.number_input("Enter weight of item (kg):", min_value=0.1, step=0.1, value=1.0)
            quantity = st.number_input("Enter Quantity of item:", min_value=1, step=1, value=1)
            if st.button("Calculate & Save", key=item_category.lower()):
                emission = calculate_kit_item_emission(item_category.lower().replace(" ", "_"), weight, quantity)
                insert_material_data(event, item_category, weight, quantity, emission)
                st.success(f"Emission for {quantity} {item_category}: {emission:.3f} kg CO₂")