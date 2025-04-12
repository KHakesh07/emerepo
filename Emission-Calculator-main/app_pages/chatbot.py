import streamlit as st
import random
import re
import sqlite3
import os

# -------------------------------
# 1. Real Data Integration: Load Emission Data from Database
# -------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR,"..", "..", "data", "emissions.db")

def load_emission_data():
    """
    Connects to your SQLite database and fetches carbon emissions data.
    
    This function aggregates data from the MasterEmissions table:
      - Total emissions as the SUM of all Emission values.
      - Breakdown into Scope 1, Scope 2, and Scope 3 (assuming these are stored under Category).
      - Category breakdown (grouped by SourceTable as a proxy).
      - Monthly aggregated emissions.
      - Reduction tips (if available from a reduction_tips_table, else default tips).
    
    Adjust the queries and table names as needed for your actual schema.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Total Emissions
    cursor.execute("SELECT SUM(Emission) FROM MasterEmissions")
    total_row = cursor.fetchone()
    total = total_row[0] if total_row and total_row[0] is not None else 0

    # Scope Breakdown: Assume Category field holds 'Scope 1', 'Scope 2', or 'Scope 3'
    scopes = {}
    for scope in ["Scope 1", "Scope 2", "Scope 3"]:
        cursor.execute("SELECT SUM(Emission) FROM MasterEmissions WHERE Category=?", (scope,))
        row = cursor.fetchone()
        scopes[scope] = row[0] if row and row[0] is not None else 0

    # Category Breakdown: Group by SourceTable as an example (adjust as needed)
    cursor.execute("SELECT SourceTable, SUM(Emission) FROM MasterEmissions GROUP BY SourceTable")
    rows = cursor.fetchall()
    categories = {row[0]: row[1] for row in rows if row[0] is not None}

    # Monthly Data: Group using SQLite's strftime function
    cursor.execute("SELECT strftime('%m', Timestamp) as month, SUM(Emission) FROM MasterEmissions GROUP BY month")
    rows = cursor.fetchall()
    monthly_data = {}
    month_lookup = {
      '01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr', '05': 'May', '06': 'Jun',
      '07': 'Jul', '08': 'Aug', '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'
    }
    for row in rows:
        month = month_lookup.get(row[0], row[0])
        monthly_data[month] = row[1] if row[1] is not None else 0

    # Reduction Tips
    try:
        cursor.execute("SELECT tip FROM reduction_tips_table")
        tips_rows = cursor.fetchall()
        reduction_tips = [r[0] for r in tips_rows]
    except sqlite3.Error:
        reduction_tips = []
    if not reduction_tips:
        reduction_tips = [
            "Use public transportation instead of driving alone",
            "Switch to LED light bulbs",
            "Reduce meat consumption, especially beef",
            "Buy locally produced goods when possible",
            "Use a programmable thermostat to reduce energy use",
            "Properly insulate your home",
            "Reduce, reuse, recycle in that order",
            "Consider offsetting your carbon footprint through verified programs"
        ]
    conn.close()
    return {
        "total": total,
        "scopes": scopes,
        "categories": categories,
        "monthly_data": monthly_data,
        "reduction_tips": reduction_tips
    }

# -------------------------------
# 2. EmissionResponseGenerator Class (Enhanced Response Logic)
# -------------------------------
class EmissionResponseGenerator:
    def __init__(self, data_source):
        self.data = data_source

    def generate_response(self, user_input, conversation_context=None):
        """Generate a rich, context-aware response based on user input."""
        input_lower = user_input.lower()

        # Check for total emissions query with detailed context.
        if ("total" in input_lower or "footprint" in input_lower) and "emission" in input_lower:
            return self._generate_total_emissions_response()

        # Scope breakdown query.
        elif "scope" in input_lower:
            return self._generate_scope_breakdown_response(user_input)

        # Category breakdown query.
        elif "category" in input_lower or "breakdown" in input_lower:
            return self._generate_category_analysis_response()

        # Reduction tips query.
        elif "reduce" in input_lower or "tip" in input_lower:
            return self._generate_reduction_tips_response()

        # Explanation query.
        elif "what is" in input_lower or "explain" in input_lower:
            return self._generate_explanation_response()

        # Fallback response for unrecognized input.
        else:
            return self._generate_fallback_response()

    def _generate_total_emissions_response(self):
        total = self.data["total"]
        scope1 = self.data["scopes"].get("Scope 1", 0)
        scope2 = self.data["scopes"].get("Scope 2", 0)
        scope3 = self.data["scopes"].get("Scope 3", 0)
        # Assume a benchmark global average (adjust this value as needed)
        average_global = 4000  
        if total < average_global * 0.8:
            comparison = "significantly lower than"
        elif total > average_global * 1.2:
            comparison = "significantly higher than"
        else:
            comparison = "close to"
        response = (f"Based on our records, your total carbon footprint is {total} kg CO₂e. "
                    f"This includes {scope1} kg CO₂e from direct emissions (Scope 1), "
                    f"{scope2} kg CO₂e from purchased energy (Scope 2), and "
                    f"{scope3} kg CO₂e from other indirect emissions (Scope 3). "
                    f"In comparison, your footprint is {comparison} the global average of approximately {average_global} kg CO₂e per year. "
                    "This detailed breakdown can help you identify which areas to focus on for reductions.")
        return response

    def _generate_scope_breakdown_response(self, user_input):
        input_lower = user_input.lower()
        if "1" in input_lower:
            val = self.data["scopes"].get("Scope 1", "unknown")
            response = (f"Scope 1 emissions, which are direct emissions from sources you control (like fuel combustion), "
                        f"are estimated at {val} kg CO₂e.")
            return response
        elif "2" in input_lower:
            val = self.data["scopes"].get("Scope 2", "unknown")
            response = (f"Scope 2 emissions, stemming from indirect energy use like purchased electricity or heat, "
                        f"are estimated at {val} kg CO₂e.")
            return response
        elif "3" in input_lower:
            val = self.data["scopes"].get("Scope 3", "unknown")
            response = (f"Scope 3 emissions, which include transportation, materials, and other indirect sources, "
                        f"are estimated at {val} kg CO₂e.")
            return response
        else:
            return ("Your emissions are grouped into Scope 1, 2, and 3. Please specify the scope you are interested in, "
                    "for example, 'Scope 2 emissions'.")

    def _generate_category_analysis_response(self):
        breakdown = ", ".join([f"{cat}: {val} kg CO₂e" for cat, val in self.data["categories"].items()])
        response = f"The emissions are also broken down by category as follows: {breakdown}. This helps pinpoint major emission sources."
        return response

    def _generate_reduction_tips_response(self):
        tips = random.sample(self.data['reduction_tips'], min(3, len(self.data['reduction_tips'])))
        tips_formatted = "\n".join([f"- {tip}" for tip in tips])
        response = f"Based on best practices, consider the following actionable tips to reduce your emissions:\n{tips_formatted}"
        return response

    def _generate_explanation_response(self):
        response = ("Carbon emissions refer to the release of carbon dioxide (CO₂) into the atmosphere—primarily "
                    "resulting from burning fossil fuels in vehicles, power plants, and industrial processes. These emissions "
                    "contribute to the greenhouse effect, leading to climate change. By understanding your carbon footprint, "
                    "you can take targeted actions to reduce your impact.")
        return response

    def _generate_fallback_response(self):
        response = ("I'm sorry, I didn't understand your question. Please ask about your total emissions, scope breakdown "
                    "(e.g., 'Scope 1'), category breakdown, reduction tips, or for an explanation of carbon emissions.")
        return response

# -------------------------------
# 3. Simple Chatbot UI Using Streamlit (Single-Interface Chat)
# -------------------------------
class EmissionChatbotWithContext:
    def __init__(self, data_source):
        self.data = data_source
        self.response_generator = EmissionResponseGenerator(data_source)

    def get_response(self, user_input, conversation_context=None):
        return self.response_generator.generate_response(user_input, conversation_context)

def chatbot_ui():
    st.write("Ask me anything about your carbon emissions and how you can reduce them with accurate, data-driven insights.")
    
    # Initialize the conversation history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm your Carbon Emissions Assistant. How can I help?"}
        ]
    
    # Initialize the chatbot with real data integration
    if "chatbot" not in st.session_state:
        data = load_emission_data()
        st.session_state.chatbot = EmissionChatbotWithContext(data)

    # Display conversation history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept new user input
    user_input = st.chat_input("Type your question here...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Generate and display a detailed response using real data
        response = st.session_state.chatbot.get_response(user_input)
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)

# -------------------------------
# 4. Run the Chatbot Application
# -------------------------------
if __name__ == "__main__":
    chatbot_ui()