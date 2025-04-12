import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
import datetime
import os
from streamlit_autorefresh import st_autorefresh

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR,"..", "..", "data", "emissions.db")



# Connect to your SQLite3 DB
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

def get_latest_event():
    """Fetch the latest event name from the Events table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM Events ORDER BY id DESC LIMIT 1")
    event = cursor.fetchone()
    return event[0] if event else None

st_autorefresh(interval=1000, key="latest_event_efresh")
event = get_latest_event()

def fetch_emissions_summary(event):
    query = """SELECT Category, SUM(Emission) as TotalEmission 
               FROM EmissionsSummary 
               WHERE Event = ? 
               GROUP BY Category"""
    return pd.read_sql_query(query, conn, params=(event,))

def draw_pie_chart(df):
    fig, ax = plt.subplots()
    ax.pie(df['TotalEmission'], labels=df['Category'], autopct='%1.1f%%')
    ax.set_title("Emissions by Scope")
    return fig

def generate_pdf(event_name, summary_df):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, f"Executive Emissions Report - {event_name}")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    y = height - 120
    total_emission = summary_df['TotalEmission'].sum()
    
    # Emission Table
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Emissions Summary:")
    y -= 20
    c.setFont("Helvetica", 12)
    for idx, row in summary_df.iterrows():
        c.drawString(60, y, f"{row['Category']}: {row['TotalEmission']:.2f} kg CO₂")
        y -= 20
    
    # Analogies
    trees = total_emission / 21  # average tree absorbs ~21kg/year
    homes = total_emission / 386  # avg monthly CO2 for a home (kg)
    car_km = total_emission / 0.2  # ~0.2 kg/km per petrol car

    y -= 20
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Impact Equivalent:")
    y -= 20
    c.setFont("Helvetica", 12)
    c.drawString(60, y, f"🌳 Trees needed to offset: {trees:.1f}")
    y -= 20
    c.drawString(60, y, f"🏠 Homes powered for 1 month: {homes:.1f}")
    y -= 20
    c.drawString(60, y, f"🚗 Kilometers driven by a car: {car_km:.1f} km")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# ---------- Streamlit UI Starts ----------
def report():
    st.title("Executive Emissions Report Generator")

    latest_event = get_latest_event()
    
    summary_df = fetch_emissions_summary(event)

    if summary_df.empty:
        st.warning("No emissions data found for the latest event.")
    else:

    # Generate PDF
        st.subheader("📥 Export Report")
        pdf_buffer = generate_pdf(latest_event, summary_df)
        st.download_button(
            label="📄 Download Executive Report (PDF)",
            data=pdf_buffer,
            file_name=f"{latest_event}_Executive_Report.pdf",
            mime='application/pdf'
        )
