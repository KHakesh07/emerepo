import os
import sqlite3
import numpy as np
import streamlit as st
import pandas as pd
import requests
from geopy.distance import geodesic
import re
import googlemaps
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import plotly.express as px
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "data", "emissions.db")

        
def fetch_latest_event():
    """Fetch the latest event name from the database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT name FROM Events ORDER BY id DESC LIMIT 1")
    event = c.fetchone()
    conn.close()
    return event[0] if event else "No events found"


# --- Google Maps API Key ---
GOOGLE_MAPS_API_KEY = "AIzaSyAr3YAZlR8CNcjPoRA4hV_ePS93bCF39EQ"

st_autorefresh(interval=1000, key="latest_event_refresh")
Event = fetch_latest_event()


# --- Function to Get Coordinates ---
def get_lat_lon(city):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={city}&key={GOOGLE_MAPS_API_KEY}"
    response = requests.get(url).json()
    if response["status"] == "OK":
        result = response["results"][0]
        location = result["geometry"]["location"]
        country = None
        for component in result["address_components"]:
            if "country" in component["types"]:
                country = component["long_name"]
                break
        return location["lat"], location["lng"], country
    else:
        print(f"Error fetching coordinates for {city}: {response.get('status')}")
    return None, None, None

def get_near_city(lat, lon):
    # use reverse geocoding api to get correct city name for coordinates
    url = f"https://maps.googleapis.com/maps/api/geocode/json"
    parms = {
        "latlng": f"{lat},{lon}",
        "key": GOOGLE_MAPS_API_KEY
    }
    response = requests.get(url, params=parms).json()

    if response["status"] == "OK":
        city_name = None
        district_name = None
        for result in response["results"]:
            for component in result["address_components"]:
                if "locality" in component["types"]:
                    city_name =  component["long_name"]
                if "administrative_area_level_2" in component["types"]:
                    district_name =  component["long_name"]
        return city_name if city_name else district_name
    return "Unknown City"


# --- Function to Find a Specific Station in a City ---
def find_city_station(city):
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": f"{city} railway station",
        "type": "train_station",
        "key": GOOGLE_MAPS_API_KEY
    }
    response = requests.get(url, params=params).json()
    if response["status"] == "OK" and response["results"]:
        station = response["results"][0]
        station_name = station["name"]
        station_lat = station["geometry"]["location"]["lat"]
        station_lon = station["geometry"]["location"]["lng"]
        return station_name, (station_lat, station_lon)
    return None, None

# --- Function to Find Nearest Transport Hub (Airport/Railway) ---
def find_nearest_place(lat, lon, place_type):
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lon}",
        "radius": 50000,  # Search within 50 km
        "type": place_type,  # "airport" or "train_station"
        "key": GOOGLE_MAPS_API_KEY
    }
    response = requests.get(url, params=params).json()
    if response["status"] == "OK" and response["results"]:
        nearest_place = response["results"][0]
        place_name = nearest_place["name"]
        place_lat = nearest_place["geometry"]["location"]["lat"]
        place_lon = nearest_place["geometry"]["location"]["lng"]
        city_name = get_near_city(place_lat, place_lon)
        return place_name, city_name, (place_lat, place_lon)
    return None, None, None

# --- Function to Get Distance between Two Places ---
def get_distance(origin, destination, mode):
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": f"{origin[0]},{origin[1]}",
        "destinations": f"{destination[0]},{destination[1]}",
        "mode": mode,  # "driving", "transit"
        "key": GOOGLE_MAPS_API_KEY
    }
    response = requests.get(url, params=params).json()

    if "rows" in response and response["rows"]:
        element = response["rows"][0]["elements"][0]
        if "status" in element:
            if element["status"] == "OK":
                return element["distance"]["text"]
            elif element["status"] == "OK":
                distance_km = round(geodesic(origin, destination).km, 2)
        elif element["status"] == "ZERO_RESULTS":
            return "No results found"
        else:
            return "Error: " + element["status"]
    return "N/A"

# --- Load OpenFlights Data ---
routes_cols = ["Airline", "Airline_ID", "Source_Airport", "Source_Airport_ID", 
               "Destination_Airport", "Destination_Airport_ID", "Codeshare", 
               "Stops", "Equipment"]

airports_cols = ["Airport_ID", "Name", "City", "Country", "IATA", "ICAO", 
                 "Latitude", "Longitude", "Altitude", "Timezone", "DST", 
                 "Tz_database", "Type", "Source"]


base1_dir = os.path.dirname(os.path.abspath(__file__))  # Get the current script directory
file_path1 = os.path.join(base1_dir, "routes.csv")

base2_dir = os.path.dirname(os.path.abspath(__file__))  # Get the current script directory
file_path2 = os.path.join(base2_dir, "airports.csv")
# Load CSV Data
routes_df = pd.read_csv(file_path1, names=routes_cols, usecols=["Source_Airport", "Destination_Airport"])
airports_df = pd.read_csv(file_path2, names=airports_cols, usecols=["Name","City", "IATA", "Latitude", "Longitude"])

# --- Match Airport Name to City in airports_df ---
def match_airport_to_city(airport_name, lat, lon):
    # Try to find a matching city based on coordinates proximity
    for _, row in airports_df.iterrows():
        dist = geodesic((lat, lon), (row["Latitude"], row["Longitude"])).km
        if dist < 50:  # Consider it a match if within 50 km
            return row["City"]
    return airport_name  # Fallback to airport name if no match

def get_air_distance_by_city(origin_city, destination_city):
    """Find airline distance between two cities using OpenFlights data."""
    origin_airport = airports_df[airports_df["City"].str.lower() == origin_city.lower()]
    destination_airport = airports_df[airports_df["City"].str.lower() == destination_city.lower()]

    if not origin_airport.empty and not destination_airport.empty:

        origin_coords = (origin_airport.iloc[0]["Latitude"], origin_airport.iloc[0]["Longitude"])
        destination_coords = (destination_airport.iloc[0]["Latitude"], destination_airport.iloc[0]["Longitude"])

        distance= round(geodesic(origin_coords, destination_coords).km, 2)
        return distance
    return None

def extract_distance(value):
    if value is None:
        return 0.0
    if isinstance(value, str):
        match = re.search(r"[\d\.]+", value)  # Find number (including decimals)
        return float(match.group()) if match else 0.0  # Convert to float
    return float(value)


def extract_rail_distance(value):
    if value is None:
        return 0.0
    if isinstance(value, str):
        match = re.search(r"[\d,]+\.?\d*", value)
        if match:
            result = float(match.group(0).replace(',', ''))
            if result < 10:  # Arbitrary threshold for suspicion
                print(f"Warning: Extracted distance {result} km seems unusually small.")
            return result
        return 0.0
    return float(value)


def insert_transport_into_db(Event, mode, type_, origin, destination, distance, emission):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO transport_data (Event, mode, type, origin, destination, distance, emission) 
                 VALUES (?, ?, ?, ?, ?, ?, ?)''', (Event, mode, type_, origin, destination, distance, emission))
    conn.commit()
    conn.close()


def display_mode_charts(travel_entries):

    mode_distance = defaultdict(float)
    mode_emission = defaultdict(float)

    # Accumulate distances and emissions by mode
    for entry in travel_entries:


        if all(k in entry for k in ["mode", "calculated_distance", "calculated_emission"]):
            mode_distance[entry["mode"]] += entry["calculated_distance"]
            mode_emission[entry["mode"]] += entry["calculated_emission"]
    
    if not mode_distance and not mode_emission:
        st.info("No valid travel data available to display charts.")
        return

    col1, col2 = st.columns(2)

    with col1:
        if mode_distance:
            st.write("### 📊 Distance by Travel Mode")
            distance_df = pd.DataFrame({
                "Mode": list(mode_distance.keys()),
                "Distance (km)": list(mode_distance.values())
            })
            fig1 = px.pie(
                distance_df, 
                names="Mode", 
                values="Distance (km)", 
                title="Distance Distribution by Mode",
                hole=0.4  # donut style for better visual distinction
            )
            fig1.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        if mode_emission:
            st.write("### 🌫️ Emission by Travel Mode")
            emission_df = pd.DataFrame({
                "Mode": list(mode_emission.keys()),
                "Emission (kgCO₂e)": list(mode_emission.values())
            })  
            fig2 = px.pie(
                emission_df, 
                names="Mode", 
                values="Emission (kgCO₂e)", 
                title="Emission Distribution by Mode",
                hole=0.4
            )
            fig2.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig2, use_container_width=True)


def travel_app():
    st.title("🚀 Multi Travel Calculator & Distance Finder")

    # Initialize session state for travel entries
    if "travel_entries" not in st.session_state:
        st.session_state.travel_entries = [
            {"id": 0, "mode": "Road", "type": "Petrol", "origin": "", "destination": "", "distance": "", "calculated_distance": "", "calculated_emission":""}
        ]


    # Iterate through travel entries
    for entry in st.session_state.travel_entries:
        index = entry["id"]
        cols = st.columns([3, 3, 3, 3, 2])  # Column layout

        with cols[0]:  # Travel Mode
            mode_options = ["Road", "Rail", "Air", "Distance"]
            default_index = mode_options.index(entry["mode"]) if entry["mode"] in mode_options else 0
            entry["mode"] = st.selectbox(f"Mode {index + 1}:", mode_options, key=f"mode_{index}", index=default_index)

        with cols[1]:  # Vehicle Type or Distance Input
            if entry["mode"] == "Road" or entry["mode"] == "Distance":
                type_options = ["Auto CNG", "Bike", "Car Petrol", "Car CNG", "Electric bike", "Electric car"]
            elif entry["mode"] == "Rail":
                type_options = ["Electric", "Diesel"]
            else:  # Distance mode - No type selection, only distance input
                type_options = ["Domestic"]

            if type_options:
                default_type_index = type_options.index(entry["type"]) if entry["type"] in type_options else 0
                entry["type"] = st.selectbox(f"Type {index + 1}:", type_options, key=f"type_{index}", index=default_type_index)

        # Origin and Destination Fields (Only for non-Distance modes)
        if entry["mode"] != "Distance":
            with cols[2]:
                entry["origin"] = st.text_input(f"Origin {index + 1}:", value=entry["origin"], key=f"origin_{index}")
            with cols[3]:
                entry['destination'] = st.text_input(f"Destination {index + 1}:", value=entry["destination"], key=f"destination_{index}")
        else:
            with cols[2]:
                entry["distance"] = st.text_input(f"Distance (km) {index + 1}:", value=entry.get("distance", ""), key=f"distance_{index}")

    # Remove Button
        with cols[4]:
            if st.button("Remove", key=f"remove_{index}"):
                st.session_state.travel_entries = [e for e in st.session_state.travel_entries if e["id"] != index]
                st.rerun()

# Button to Add New Travel Entry
    if st.button("Add Another Travel Entry"):
        new_id = max([e["id"] for e in st.session_state.travel_entries]) + 1 if st.session_state.travel_entries else 0
        st.session_state.travel_entries.append({"id": new_id, "mode": "Road", "type": "Petrol", "origin": "", "destination": "", "distance": ""})
        st.rerun()


    # Calculate Distance for Each Entry and Total
    if st.button("Calculate Distance"):
        total_distance = 0.0  # Initialize total distance accumulator
        total_emission = 0.0
        st.write("### Travel Distances")

        for entry in st.session_state.travel_entries:
            
            if entry["mode"] != "Distance" and not (entry["origin"].strip() and entry["destination"].strip()):
                st.warning("Please enter both origin and destination.")
                continue

            origin_lat, origin_lon, origin_country = get_lat_lon(entry["origin"])
            dest_lat, dest_lon, dest_country = get_lat_lon(entry["destination"])
        

            if entry["mode"] in ["Rail", "Road"] and (origin_country != "India" or dest_country != "India"):
                st.warning(f"{entry['mode']} travel is limited to India only. {entry['origin']} ({origin_country}) or {entry['destination']} ({dest_country}) is outside India.")
                continue
            origin_coords = (origin_lat, origin_lon)
            dest_coords = (dest_lat, dest_lon)

            if entry["mode"] == "Distance":
                st.write(f"📏 **Distance travelled**: {entry['distance']} km")
                emission_dist = 0.0
                distance_value = float(entry['distance'])
        
                if entry["type"] == "Auto CNG":
                    emission_dist = distance_value * 0.107
                elif entry["type"] == "Bike":
                    emission_dist = distance_value * 0.049
                elif entry["type"] == "Car Petrol":
                    emission_dist = distance_value * 0.187
                elif entry["type"] == "Electric bike":
                    emission_dist = distance_value * 0.031
                elif entry["type"] == "Car CNG":
                    emission_dist = distance_value * 0.68
                else:
                    emission_dist = round(distance_value * 0.012, 3)

                st.write(f"🚉 Emission calculated for {entry['distance']} km is {round(emission_dist,3)} kgCO₂e")
                total_distance += distance_value
                total_emission += emission_dist
                continue  

            if origin_coords and dest_coords:
                if entry["mode"] == "Air":
                    origin_airport, origin_city, origin_airport_coords = find_nearest_place(*origin_coords, "airport")
                    dest_airport, dest_city, dest_airport_coords = find_nearest_place(*dest_coords, "airport")

                    if origin_airport and dest_airport and origin_airport_coords and dest_airport_coords:
                        to_airport = round(extract_distance(get_distance(origin_coords, origin_airport_coords, "driving")), 2)
                        air_distance_result = get_air_distance_by_city(origin_city, dest_city)  # Use matched cities
                        if air_distance_result is None:
                            st.success("Using nearest airports distance.")                                
                            air_distance = round(geodesic(origin_airport_coords, dest_airport_coords).km, 2)
                        else:
                            air_distance = round(air_distance_result, 2)
                        from_airport = round(extract_distance(get_distance(dest_airport_coords, dest_coords, "driving")), 2)

                        distance_value = round(to_airport + air_distance + from_airport, 2)
                        total_distance += distance_value
                        emission_dist = round(air_distance*1.58, 2)
                        total_emission += emission_dist

                        st.success(f"✈️ **Flight Distance**:")
                        st.write(f"🚗 {entry['origin']} → {origin_airport}: {to_airport} km")
                        st.write(f"✈️ {origin_airport} → {dest_airport}: {air_distance} km")
                        st.write(f"🚗 {entry['destination']} ← {dest_airport}: {from_airport} km")
                        st.write(f"📏 **Trip AIR Total**: {distance_value} km")
                        st.write(f"Emission for air distance: {emission_dist} kgco2e")

                    else:
                        st.warning(f"Could not fetch location data for {entry['origin']} or {entry['destination']}.")

                elif entry["mode"] == "Rail":
                    origin_station, origin_station_coords = find_city_station(entry["origin"])
                    if not origin_station:
                        origin_station, origin_city, origin_station_coords = find_nearest_place(*origin_coords, "train_station")
                        if not origin_station:
                            st.warning(f"No railwaystation found near {entry['origin']}.")
                    dest_station, dest_station_coords = find_city_station(entry["destination"])
                    if not dest_station:
                        dest_station, dest_city, dest_station_coords = find_nearest_place(*dest_coords, "train_station")
                        if not dest_station:
                            st.warning(f"No railwaystation found near {entry['destination']}.")

                    if origin_station and dest_station:
                        rail_distance = get_distance(origin_station_coords, dest_station_coords, "transit")
                        distance_value = round(extract_rail_distance(rail_distance), 4)
                        total_distance += distance_value  # Add to total

                        st.success(f"🚆 **Rail Distance**:")
                        st.write(f"🚉 **{origin_station} → {dest_station}**: {distance_value} km")
                        emission_dist = round(0.0,3)
                        if entry["type"] == "Electric":
                            emission_dist = round(distance_value*0.82,3)
                            st.write(f"🚉 Emission for Electric  rail from **{origin_station} → {dest_station}**: {emission_dist} kgco2e")
                        else:
                            emission_dist = distance_value*2.651
                            st.write(f"🚉 Emission Diesel rail from **{origin_station} → {dest_station}**: {emission_dist} kgco2e")
                        total_emission += emission_dist
                    else:
                        st.warning("Could not find nearby railway stations.")
                

                else:  # Road Mode
                    road_distance = get_distance(origin_coords, dest_coords, "driving")
                    distance_value = round(extract_distance(road_distance), 2)
                    total_distance += distance_value  # Add to total

                    st.write(f"🚗 Road Distance from {entry['origin']} → {entry['destination']}: {distance_value} km")
                    emission_dist = 0.0
                    if entry["type"] == "Auto CNG":
                        emission_dist = distance_value*0.107
                    elif entry["type"] == "Bike":
                        emission_dist = distance_value*0.049
                    elif entry["type"] == "Car Petrol":
                        emission_dist = distance_value*0.187
                    elif entry["type"] == "Electric bike":
                        emission_dist = distance_value*0.031
                    elif entry["type"] == "Car CNG":
                        emission_dist = distance_value*0.68
                    else:
                        emission_dist = distance_value * 0.012
                    st.write(f"🚉 Emission from  {entry['origin']} → {entry['destination']} is {round(emission_dist,3)} kgco2e")
                    total_emission += emission_dist
                    
    
            else:
                st.warning(f"Could not fetch location data for {entry['origin']} or {entry['destination']}.")
        entry["calculated_distance"] = distance_value
        entry["calculated_emission"] = emission_dist
    # Display the total distance across all entries
        total_distance = round(total_distance, 2)  # Round the final total
        total_emission = round(total_emission, 2)
        if total_distance > 0 and total_emission > 0:
            st.write("---")
            st.success(f"🌍 **Total Distance Across All Trips**: {total_distance} km")
            st.success(f"🌍 **Total Emission Across All Trips**: {total_emission} kgco2e")
            insert_transport_into_db(Event, entry["mode"], entry["type"], entry["origin"], entry['destination'], distance_value, emission_dist)
            display_mode_charts(st.session_state.travel_entries)
        else:
            st.info("No valid distances calculated.")



