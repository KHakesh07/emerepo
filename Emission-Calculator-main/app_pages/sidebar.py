import streamlit as st
from app_pages.chatbot import chatbot_ui

def render_sidebar(username):
    """Render the complete sidebar with functional components and enhanced UI."""
    # Apply custom styling for an attractive sidebar
    st.sidebar.markdown("""
    <style>
        /* Overall sidebar styling */
        [data-testid="stSidebar"] {
            background-image: linear-gradient(to bottom, #1e293b, #0f172a);
            padding-top: 1rem;
        }
        
        /* Welcome header styling */
        .welcome-header {
            color: #ffffff;
            font-size: 1.5rem;
            margin-bottom: 1.5rem;
            padding-left: 0.5rem;
            border-left: 4px solid #4e8cff;
        }
        
        /* Button styling */
        .nav-button {
            background-color: rgba(78, 140, 255, 0.1);
            border-radius: 8px;
            padding: 10px 15px;
            margin: 5px 0;
            transition: all 0.3s;
            color: #ffffff;
            border: 1px solid rgba(78, 140, 255, 0.2);
            width: 100%;
            display: flex;
            align-items: center;
        }
        
        .nav-button:hover {
            background-color: rgba(78, 140, 255, 0.3);
            border-color: rgba(78, 140, 255, 0.5);
            transform: translateY(-2px);
        }
        
        .nav-button-icon {
            margin-right: 10px;
            color: #4e8cff;
        }
        
        /* Divider styling */
        .sidebar-divider {
            margin: 1.5rem 0;
            height: 1px;
            background: linear-gradient(to right, rgba(78, 140, 255, 0), rgba(78, 140, 255, 0.5), rgba(78, 140, 255, 0));
        }
        
        /* Chatbot section */
        .chatbot-header {
            font-weight: bold;
            font-size: 1.1rem;
            color: #ffffff;
            margin-bottom: 1rem;
            padding-left: 0.5rem;
            border-left: 4px solid #4e8cff;
            background-color: rgba(78, 140, 255, 0.1);
            padding: 10px;
            border-radius: 6px;
        }
        
        /* User info container */
        .user-info-container {
            background-color: rgba(78, 140, 255, 0.1);
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 1.5rem;
            border: 1px solid rgba(78, 140, 255, 0.2);
        }
        
        /* User details */
        .user-role {
            font-size: 0.9rem;
            opacity: 0.8;
            margin-bottom: 0.5rem;
        }
        
        /* Tooltip styling */
        .tooltip {
            position: relative;
            display: inline-block;
        }
        
        .stButton button {
            width: 100%;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # User profile info section
    st.sidebar.markdown(f"""
    <div class="user-info-container">
        <div class="welcome-header">Welcome, {username}</div>
        <div class="user-role">{get_role_from_username(username)}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Create session state for navigation if it doesn't exist
    if "sidebar_page" not in st.session_state:
        st.session_state.sidebar_page = "main"
    
    # Main sidebar navigation when not in profile or contact pages
    if st.session_state.sidebar_page == "main":
        # Navigation buttons with icons
        if st.sidebar.button("👤 Profile", key="profile_button", use_container_width=True, 
                           help="View and edit your profile"):
            st.session_state.sidebar_page = "profile"
            st.rerun()
            
        if st.sidebar.button("✉️ Contact Us", key="contact_button", use_container_width=True,
                           help="Get support or ask questions"):
            st.session_state.sidebar_page = "contact"
            st.rerun()
        
        # Analytics metrics summary
        st.sidebar.markdown("""<div class="sidebar-divider"></div>""", unsafe_allow_html=True)
        st.sidebar.markdown("### Quick Stats")
        
        # Display key metrics
        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.metric(label="Carbon Footprint", value="72.5 mt", delta="-2.3%")
        with col2:
            st.metric(label="Target Progress", value="68%", delta="+4%")
        
        # Add divider before the chatbot
        st.sidebar.markdown("""<div class="sidebar-divider"></div>""", unsafe_allow_html=True)
        st.sidebar.markdown("""<div class="chatbot-header">💬 Carbon Emissions Assistant</div>""", unsafe_allow_html=True)
        
        # Render the chatbot interface in the sidebar
        with st.sidebar:
            chatbot_ui()
        
        # Logout button at bottom
        st.sidebar.markdown("""<div class="sidebar-divider"></div>""", unsafe_allow_html=True)
        if st.sidebar.button("🚪 Logout", key="logout_button", use_container_width=True,
                           help="End your session"):
            if "logged_in_user" in st.session_state:
                del st.session_state.logged_in_user
            st.markdown("<meta http-equiv='refresh' content='0'>", unsafe_allow_html=True)
    
    # Profile page view
    elif st.session_state.sidebar_page == "profile":
        if st.sidebar.button("← Back to Dashboard", use_container_width=True):
            st.session_state.sidebar_page = "main"
            st.rerun()
        
        # Display profile content in the main area
        show_profile(username)
    
    # Contact us page view
    elif st.session_state.sidebar_page == "contact":
        if st.sidebar.button("← Back to Dashboard", use_container_width=True):
            st.session_state.sidebar_page = "main"
            st.rerun()
        
        # Display contact form in the main area
        show_contact_us()

# Keep the other functions as they are
def show_profile(username):
    """Display user profile information."""
    st.header("User Profile")
    
    # User information
    st.subheader("Personal Information")
    cols = st.columns([1, 2])
    with cols[0]:
        # Profile picture placeholder
        st.image("https://via.placeholder.com/150", width=120)
    
    with cols[1]:
        st.write(f"**Username:** {username}")
        st.write(f"**Role:** {get_role_from_username(username)}")
        st.write("**Last Login:** Today at 9:30 AM")
    
    # User preferences section
    st.subheader("Preferences")
    st.write("**Dashboard Theme:** Dark")
    st.write("**Notifications:** Enabled")
    
    # Recent activity
    st.subheader("Recent Activity")
    st.info("Analyzed Scope 1 emissions - Today at 10:15 AM")
    st.info("Generated monthly report - Yesterday at 2:30 PM")
    st.info("Updated electricity consumption data - 3 days ago")

def show_contact_us():
    """Display contact information and support options."""
    st.header("Contact Us")
    
    # Company information section
    st.subheader("Company Information")
    st.write("**Email:** support@emissionscalculator.com")
    st.write("**Phone:** +1 (555) 123-4567")
    st.write("**Hours:** Monday-Friday, 9:00 AM - 5:00 PM EST")
    
    # Support options
    st.subheader("Get Support")
    support_type = st.selectbox(
        "How can we help you?",
        ["Technical Support", "Feature Request", "Bug Report", "General Inquiry"]
    )
    
    st.text_area("Describe your issue or question:", height=150)
    st.text_input("Your Email (for response):")
    
    if st.button("Submit Request", type="primary"):
        st.success("Your request has been submitted! Our team will get back to you within 24 hours.")
    
    # FAQ section
    st.subheader("Frequently Asked Questions")
    with st.expander("How is the carbon footprint calculated?"):
        st.write("""
        Our calculator uses internationally recognized emission factors and methodologies 
        to convert activity data into greenhouse gas emissions. We follow the GHG Protocol 
        standards for accurate accounting across all three scopes.
        """)
    
    with st.expander("Can I export my emissions data?"):
        st.write("""
        Yes! You can export your data in various formats including CSV, Excel, and PDF. 
        Look for the export button at the top right corner of each dashboard section.
        """)
    
    with st.expander("How often should I update my emissions data?"):
        st.write("""
        For the most accurate reporting, we recommend monthly updates. However, 
        the frequency may depend on your organization's size and reporting requirements.
        """)

def get_role_from_username(username):
    """Maps username to role title."""
    role_mapping = {
        "ops_manager": "Operations Manager",
        "event_coordinator": "Event Coordinator",
        "sustain_consultant": "Sustainability Consultant"
    }
    return role_mapping.get(username, "User")