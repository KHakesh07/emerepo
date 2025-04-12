import sqlite3
import streamlit as st
import pandas as pd
import plotly.express as px
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from streamlit_autorefresh import st_autorefresh
import logging
import os
import requests

GOOGLE_MAPS_API_KEY = st.secrets["google"]["maps_api_key"]
# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR,"..", "..", "data", "emissions.db")


def fetch_latest_event():
    """Fetch the latest event name from the database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT name FROM Events ORDER BY id DESC LIMIT 1")
    event = c.fetchone()
    conn.close()
    return event[0] if event else "No events found"

Event = fetch_latest_event()


def store_logistics_data(Event, material, transport_mode, origin, destination, distance, weight, total_emission):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO logistics_emissions 
            (Event, material, transport_mode, origin, destination, distance_km, weight_kg, total_emission) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (Event, material, transport_mode, origin, destination, distance, weight, total_emission))
        
        conn.commit()
        conn.close()
        st.success("✅ Data inserted successfully!")
    except sqlite3.Error as e:
        st.warning(f"❌ Database error: {e}")

def get_distance_google_maps(origin, destination):
    try:
        url = f"https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&origins={origin}&destinations={destination}&key={GOOGLE_MAPS_API_KEY}"
        response = requests.get(url)
        data = response.json()

        if data["status"] == "OK":
            distance_text = data["rows"][0]["elements"][0]["distance"]["text"]
            distance_km = float(distance_text.replace(" km", "").replace(",", ""))
            return round(distance_km, 2)
        else:
            st.error("Google Maps API error: " + data.get("error_message", "Unknown error"))
            return None
    except Exception as e:
        st.error(f"Error fetching distance: {e}")
        return None

def calculate_air_distance(origin, destination):
    geolocator = Nominatim(user_agent="logistics_app")
    try:
        origin_loc = geolocator.geocode(origin)
        destination_loc = geolocator.geocode(destination)
        if origin_loc and destination_loc:
            origin_coords = (origin_loc.latitude, origin_loc.longitude)
            destination_coords = (destination_loc.latitude, destination_loc.longitude)
            return round(geodesic(origin_coords, destination_coords).km, 2)
        else:
            return None
    except Exception as e:
        st.error(f"Error getting coordinates: {e}")
        return None



# Constants
EMISSION_FACTOR = 1.58  # Emission factor per km per kg

# Transport modes and efficiency
TRANSPORT_MODES = {
    "Truck": {"profile": "driving-car", "efficiency": 1.9},
    "Rail": {"profile": "driving-hgv", "efficiency": 0.6},  # Heavy Goods Vehicle as a proxy
    "Air": {"profile": None, "efficiency": 3.0}  # Geodesic Distance for Air
}



# Streamlit UI
def logist_calculator():
    """Display the logistics emission calculator."""
    st.title("📦 Logistics Emission Calculator")
    st.write("Event: ", Event)
    st.subheader("computeing CO₂ emissions for logistics transportation")

    # User Inputs
    material = st.text_input("Enter Materials", "Tables")
    transport_mode = st.selectbox("Select Transport Mode", list(TRANSPORT_MODES.keys()))
    origin = st.text_input("Enter Origin City", "Delhi")
    destination = st.text_input("Enter Destination City", "Mumbai")
    weight = st.number_input("Enter Material Weight (kg)", min_value=1, value=1000)

    # Compute Distance
    distance = None
    if st.button("Calculate Distance"):
        if transport_mode == "Air":
            distance = calculate_air_distance(origin, destination)  # You can use haversine here
        else:
            distance = get_distance_google_maps(origin, destination)

    # Compute Emission
    if distance:
        efficiency_factor = TRANSPORT_MODES[transport_mode]["efficiency"]
        total_emission = round(distance * weight * EMISSION_FACTOR * efficiency_factor, 2)
        

        # Display Metrics
        st.metric(label="Total CO₂ Emission (kg)", value=total_emission)
        store_logistics_data(Event, material, transport_mode, origin, destination, distance, weight, total_emission)
        st.success(f"Transporting {weight} kg of {material} from {origin} to {destination} via {transport_mode} emits **{total_emission} kg CO₂**. and the distance is **{distance} km**.")

# Run the app
if __name__ == "__main__":
    logist_calculator()