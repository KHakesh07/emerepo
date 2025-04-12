import os
import streamlit as st
import sqlite3
import time
import qrcode
from io import BytesIO
from logistics import travel_app
from streamlit_autorefresh import st_autorefresh

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

Event = fetch_latest_event()
col3, col4, col5 = st.columns(3)
with col3:
    if st.button("Refresh Event", key="r_event"):
        Event = fetch_latest_event()
        st.success("Event refreshed successfully!")
with col4:
    st.write(" ")
with col5:
    st.write(f"Event name: {Event}")

def store_food_data(Event, session_id, dietary_pattern, food_choices, emission):
    """Store food choices for the user session."""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        for food_item in food_choices:
            emission = emission_factors.get(food_item, 0.0)  # Get per-item emission
            c.execute('''INSERT INTO food_choices (Event, session_id, dietary_pattern, food_item , emission) 
                 VALUES (?, ?, ?, ?, ?)''', (Event, session_id, dietary_pattern, food_item, emission))
        conn.commit()


def store_message(Event, name, message):
    """Save a user's contact message to the database."""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO contact_messages (name, message) VALUES (?, ?, ?)", (Event, name, message))
        conn.commit()



# Define the URL for your app (replace with your actual app URL)
app_url = "https://transport-food-data-collection-pzksckdswfrpqjusoctcx5.streamlit.app/"

# Generate the QR code for your app URL
qr = qrcode.make(app_url)
buf = BytesIO()
qr.save(buf, format="PNG")
buf.seek(0)

# Create a session ID for each user (used to store data separately)
if "session_id" not in st.session_state:
    # Using time.time() to generate a session id; consider uuid.uuid4() for randomness.
    st.session_state.session_id = str(time.time())
    print(f"[DEBUG] New session ID generated: {st.session_state.session_id}")
else:
    print(f"[DEBUG] Using existing session ID: {st.session_state.session_id}")

# Sidebar Navigation
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/149/149071.png", width=60)
    st.title("🚀 Menu")
    option = st.radio("Go to", ["Home", "Scan QR", "Transport", "Food", "View Data", "Contact Us"])

# Main Container for Display
with st.container():
    st.markdown("<div style='max-width: 360px; margin: auto;'>", unsafe_allow_html=True)
    
    # Home Page
    if option == "Home":
        st.header("🌍 Welcome to the Event Emissions Data Collector!")
        st.write(
            "We developed a dashboard using Streamlit that displays **Scope 1, 2, and 3 emissions** for an event. "
            "This web application allows event attendees to submit transportation and food data."
        )
        cols = st.columns(3)


        st.subheader("📌 What You Can Do Here:")
        st.markdown(""" 
        - ✅ **Enter Transportation Details** – Specify your mode of travel and distance traveled.
        - ✅ **Choose Your Food Preference** – Select from Veg, Non-Veg, or Vegan options.
        """)
        st.write("Use the sidebar to navigate.")

    # QR Code Page
    elif option == "Scan QR":
        st.header("📱 Scan this QR Code")
        st.write("Scan this QR code to open the app on your mobile device.")
        st.image(buf, caption="Scan me!", use_container_width=True)

    # Transport Data Collection
    elif option == "Transport":
        travel_app()
        
    # Food Preferences Data Collection
    elif option == "Food":
        st.header("🍽 Select Your Food Preferences")
    
        # Dietary Pattern Selection
        dietary_pattern = st.radio(
            "Select Your Dietary Pattern", 
            ["Vegetarian Diet", "Non-Vegetarian Diet (with Mutton)", "Non-Vegetarian Diet (with Chicken)"]
        )
    
        # Food Items Based on Dietary Pattern
        if dietary_pattern == "Vegetarian Diet":
            food_items = ["Chapatti (Wheat Bread)", "Rice", "Pulses (Lentils)", "Vegetables (Cauliflower, Brinjal)"]
        elif dietary_pattern == "Non-Vegetarian Diet (with Mutton)":
            food_items = ["Chapatti (Wheat Bread)", "Rice", "Pulses (Lentils)", "Vegetables (Cauliflower, Brinjal)", "Mutton"]
        elif dietary_pattern == "Non-Vegetarian Diet (with Chicken)":
            food_items = ["Chapatti (Wheat Bread)", "Rice", "Pulses (Lentils)", "Vegetables (Cauliflower, Brinjal)", "Chicken"]

        selected_food_items = st.multiselect("Food Items", food_items)
        breakfast_selection = st.multiselect("Choose your Breakfast options", 
                                             ["Milk", "Eggs", "Idli with Sambar", "Poha with Vegetables", 
                                              "Paratha with Curd", "Upma", "Omelette with Toast", 
                                              "Masala Dosa", "Puri Bhaji", "Aloo Paratha", "Medu Vada", 
                                              "Sabudana Khichdi", "Dhokla", "Chole Bhature", 
                                              "Besan Cheela", "Pongal"])
        salad_selection = st.multiselect("Choose your Salads", 
                                         ["Kachumber Salad", "Sprouted Moong Salad", "Cucumber Raita Salad", 
                                          "Tomato Onion Salad", "Carrot and Cabbage Salad"])
        sweets_selection = st.multiselect("Choose your Sweets", 
                                          ["Gulab Jamun", "Rasgulla", "Kheer", "Jalebi", "Kaju Katli", 
                                           "Barfi", "Halwa (Carrot or Bottle Gourd)", "Laddu"])
        banana_selection = "Single Banana"  # This is a fixed option
        
        # Flatten the selections (remove extra list brackets)
        user_choices = list(selected_food_items) + list(breakfast_selection) + list(salad_selection) + list(sweets_selection) + list([banana_selection])

        emission_factors = {
            "Vegetarian Diet": 0.723, "Non-Vegetarian Diet": 1.30, "Vegan Diet": 0.7,
            "Milk": 0.729, "Eggs": 0.588, "Idli with Sambar": 0.61, "Poha with Vegetables": 0.71,
            "Paratha with Curd": 0.49, "Upma": 0.28, "Omelette with Toast": 0.419,
            "Masala Dosa": 0.58, "Puri Bhaji": 1.2, "Aloo Paratha": 0.40,
            "Medu Vada": 1.5, "Sabudana Khichdi": 1.0, "Dhokla": 0.8,
            "Chole Bhature": 1.1, "Besan Cheela": 0.7, "Pongal": 0.6,
            "Kachumber Salad": 0.4, "Sprouted Moong Salad": 0.3,
            "Cucumber Raita Salad": 0.2, "Tomato Onion Salad": 0.3,
            "Carrot and Cabbage Salad": 0.25, "Gulab Jamun": 0.725, "Rasgulla": 0.725,
            "Kheer": 0.348, "Jalebi": 0.07, "Kaju Katli": 0.065, "Barfi": 0.069,
            "Halwa (Carrot or Bottle Gourd)": 0.11, "Laddu": 0.040, "Single Banana": 0.1
        }
        total_food_emission = 0.0
        for item in list(user_choices):
            emission = emission_factors.get(item, 0.0)
            total_food_emission += emission

        # Round only once, after loop
            total_food_emission = round(total_food_emission, 3)

        if st.button("Save Food Preferences", key="LKG"):
            if user_choices:
                # Display all selected items with their emissions
                st.write("### 🍽️ Selected Food Items and Emissions:")
                for item in user_choices:
                    st.write(f"- {item}: {emission_factors.get(item, 0.0)} kgCO₂e")

        # Save the full list and total emission
                store_food_data(Event, st.session_state.session_id, dietary_pattern, user_choices, total_food_emission)
                st.write("**Total Emission:**", total_food_emission, "kgCO₂e")
                st.success("✅ Food preferences saved!")
            else:
                st.warning("⚠️ Please select at least one food item.")

    # View Submitted Data
    elif option == "View Data":
        st.header("📊 Your Submitted Data")
        conn =  sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute("SELECT mode, distance FROM transport_data WHERE Event = ?", (Event,))
        transport_data = c.fetchall()
        c.execute("SELECT food_item FROM food_choices WHERE Event = ?", (Event,))
        food_data = c.fetchall()
        conn.close()
        
        if transport_data:
            st.subheader("🚗 Transport Details")
            for entry in transport_data:
                st.write(f"**Mode:** {entry[0]}, **Distance:** {entry[1]} km" )
        else:
            st.write("No transport data available.")
        
        if food_data:
            st.subheader("🍽 Food Preference")
            for food in food_data:
                st.write(f"**Preference:** {food[0]}")
        else:
            st.write("No food data available.")

    # Contact Us Page
    elif option == "Contact Us":
        st.header("📞 Contact Us")
        name = st.text_input("Your Name")
        message = st.text_area("Your Message")
        if st.button("Send Message"):
            # Uncomment the following line if store_message is defined in db.py and imported
            # store_message(name, message)
            st.success("✅ Your message has been sent!")
            store_message(Event, name, message)

    st.markdown("</div>", unsafe_allow_html=True)




