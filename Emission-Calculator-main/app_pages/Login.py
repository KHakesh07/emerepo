import streamlit as st
import logging
import os
from hashlib import sha256
import time
from datetime import datetime
import base64
import json

st.set_page_config(layout="wide")

# Configure logging with rotation
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(module)s - %(message)s",
    handlers=[
        logging.FileHandler("app_logs.log"),
        logging.StreamHandler()
    ]
)

# Environment variables for sensitive data with fallbacks to a secure config
def load_credentials():
    """Load credentials from environment variables or secure config"""
    # Try to load from environment variables first
    credentials = {
        "ops_manager": os.getenv("OPS_MANAGER_PASSWORD"),
        "event_coordinator": os.getenv("EVENT_COORDINATOR_PASSWORD"),
        "sustain_consultant": os.getenv("SUSTAIN_CONSULTANT_PASSWORD"),
    }
    
    # If any credentials are missing, try to load from config file
    if None in credentials.values():
        try:
            config_path = os.path.join(os.path.dirname(__file__), 'secure_config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    file_credentials = json.load(f)
                    # Update missing credentials
                    for key, value in credentials.items():
                        if value is None and key in file_credentials:
                            credentials[key] = file_credentials[key]
        except Exception as e:
            logging.error(f"Error loading credentials from file: {e}")
    
    # Apply defaults for any still-missing credentials (for development only)
    for key in credentials:
        if credentials[key] is None:
            credentials[key] = "admin123"
            logging.warning(f"Using default password for {key} - NOT SECURE for production!")
    
    return credentials

# Load user credentials
USER_CREDENTIALS = load_credentials()

# Security functions
def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    salt = os.getenv("PASSWORD_SALT", "sustainability_platform")
    salted = (password + salt).encode()
    return sha256(salted).hexdigest()

def verify_password(stored_hash, provided_password):
    """Verify a password against its hash."""
    return stored_hash == hash_password(provided_password)

# Login attempt tracking for rate limiting
login_attempts = {}

def check_rate_limit(username):
    """Check if the user has exceeded login attempts"""
    current_time = time.time()
    if username in login_attempts:
        attempts = [t for t in login_attempts[username] if current_time - t < 300]  # 5 min window
        login_attempts[username] = attempts
        
        if len(attempts) >= 5:
            return False  # Rate limited
    else:
        login_attempts[username] = []
    
    return True  # Not rate limited

def record_login_attempt(username):
    """Record a login attempt for rate limiting"""
    current_time = time.time()
    if username in login_attempts:
        login_attempts[username].append(current_time)
    else:
        login_attempts[username] = [current_time]

# CSS styles for the login UI
def load_css():
    st.markdown("""
    <style>
        /* Login Header */
        .login-header {
            color: #ffffff;
            font-size: 1.4rem;
            margin-bottom: 15px;
            border-left: 4px solid #4e8cff;
            padding-left: 10px;
        }
        
        /* Input Fields */
        .stTextInput>div>div>input, .stSelectbox>div>div>div {
            background-color: rgba(45, 55, 72, 0.5);
            color: white;
            border: 1px solid rgba(78, 140, 255, 0.3);
            border-radius: 5px;
            padding: 10px;
            transition: all 0.3s;
        }
        
        .stTextInput>div>div>input:focus, .stSelectbox>div>div>div:focus {
            border-color: #4e8cff;
            box-shadow: 0 0 0 2px rgba(78, 140, 255, 0.2);
        }
        
        /* Login Button */
        .stButton button {
            background-color: #4e8cff;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 10px 24px;
            font-weight: bold;
            transition: all 0.3s;
            width: 100%;
            margin-top: 10px;
        }
        
        .stButton button:hover {
            background-color: #3a7aff;
            box-shadow: 0 4px 12px rgba(78, 140, 255, 0.3);
            transform: translateY(-2px);
        }
        
        /* Error and Success Messages */
        .login-error {
            background-color: rgba(220, 38, 38, 0.1);
            color: #f87171;
            border-left: 4px solid #dc2626;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            font-size: 0.9rem;
        }
        
        .login-success {
            background-color: rgba(34, 197, 94, 0.1);
            color: #86efac;
            border-left: 4px solid #22c55e;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            font-size: 0.9rem;
        }
        
        .login-logo {
            display: flex;
            justify-content: center;
            margin-bottom: 15px;
        }

        .login-logo img {
            max-width: 240px;
            height: auto;
        }
        
        /* Loading indicator */
        .login-loading {
            display: flex;
            justify-content: center;
            margin: 15px 0;
        }
        
        /* Role selector styling */
        .role-selector {
            margin-bottom: 15px;
        }
        
        /* Forgot password link */
        .forgot-password {
            text-align: right;
            margin-top: 5px;
            margin-bottom: 15px;
            font-size: 0.8rem;
        }
        
        .forgot-password a {
            color: #93c5fd;
            text-decoration: none;
        }
        
        .forgot-password a:hover {
            color: #4e8cff;
            text-decoration: underline;
        }
        
        /* Remember me checkbox */
        .remember-me {
            display: flex;
            align-items: center;
            margin-top: 10px;
            margin-bottom: 15px;
        }
        
        .remember-me input {
            margin-right: 8px;
        }
        
        /* Custom selectbox arrow */
        .stSelectbox div[data-baseweb="select"] > div {
            background-color: rgba(45, 55, 72, 0.5) !important;
            border-color: rgba(78, 140, 255, 0.3) !important;
        }
        
        /* Help text */
        .login-help {
            font-size: 0.8rem;
            color: #94a3b8;
            text-align: center;
            margin-top: 15px;
        }
                
        /* divider */
        .logo-divider {
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(78, 140, 255, 0.5), transparent);
            margin: 10px 0 20px 0;
            border: none;
        }
    </style>
    """, unsafe_allow_html=True)

def render_login_logo():
    """Render the logo in the sidebar with divider"""
    logo_url = "https://animations.fossee.in/static/img/fossee_logo_iitb.png"
    
    st.sidebar.markdown(f"""
    <div class="login-logo">
        <img src="{logo_url}" alt="IIT Bombay Logo">
    </div>
    <hr class="logo-divider">
    """, unsafe_allow_html=True)

def show_login_error(message):
    st.sidebar.markdown(f"""
    <div class="login-error">
        <strong>⚠️ Error:</strong> {message}
    </div>
    """, unsafe_allow_html=True)

def show_login_success(message):
    st.sidebar.markdown(f"""
    <div class="login-success">
        <strong>✓ Success:</strong> {message}
    </div>
    """, unsafe_allow_html=True)

def show_loading():
    st.sidebar.markdown("""
    <div class="login-loading">
        <div class="spinner"></div>
    </div>
    """, unsafe_allow_html=True)

##############################################
# Enhanced Login with Role Selection (in Sidebar)
##############################################
def simple_login():
    """
    Enhanced login function with attractive UI and improved security.
    Note: Function name kept as 'simple_login' for backward compatibility.
    """
    # Apply custom CSS
    load_css()
    
    # If already logged in, immediately return the stored user
    if "logged_in_user" in st.session_state and st.session_state.logged_in_user:
        return st.session_state.logged_in_user
    
    # App logo
    render_login_logo()
    
    # Login header
    st.sidebar.markdown('<div class="login-header">Sign In</div>', unsafe_allow_html=True)
    
    # Role selection from a drop-down
    role = st.sidebar.selectbox(
        "Select Your Role:",
        options=["Operations Manager", "Event Coordinator", "Sustainability Consultant"],
        key="login_role"
    )
    
    # Map role selection to the expected username
    role_mapping = {
        "Operations Manager": "ops_manager",
        "Event Coordinator": "event_coordinator",
        "Sustainability Consultant": "sustain_consultant"
    }

    # Username and password input fields
    username = st.sidebar.text_input("Username:", value="", key="login_username").strip().lower()
    password = st.sidebar.text_input("Password:", type="password", key="login_password")
    
    # Remember me checkbox and forgot password link
    cols = st.sidebar.columns([3, 2])
    with cols[0]:
        remember_me = st.checkbox("Remember me", key="remember_me")
    
    with cols[1]:
        st.markdown("""
        <div class="forgot-password">
            <a href="#" onclick="alert('Please contact your administrator to reset your password.');">Forgot password?</a>
        </div>
        """, unsafe_allow_html=True)
    
    # Login button
    login_button = st.sidebar.button("Sign In", key="login_button", use_container_width=True)
    
    # Help text
    st.sidebar.markdown("""
    <div class="login-help">
        Having trouble signing in? Contact support at<br/>
        support@emissionscalculator.com
    </div>
    """, unsafe_allow_html=True)
    
    # Close login container
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # Process login
    if login_button:
        if not username or not password:
            show_login_error("Username and password are required.")
            return None
        
        # Check rate limiting for this username
        if not check_rate_limit(username):
            show_login_error("Too many failed attempts. Please try again in 5 minutes.")
            return None
        
        # Record the login attempt
        record_login_attempt(username)
        
        # Authentication logic
        expected_username = role_mapping[role]
        expected_password_hash = hash_password(USER_CREDENTIALS.get(expected_username, ""))
        
        # Add a small delay to prevent timing attacks
        time.sleep(0.5)
        show_loading()
        
        if username == expected_username and verify_password(expected_password_hash, password):
            # Successful login
            show_login_success(f"Successfully logged in as {role}")
            
            # Store user info in session state
            st.session_state.logged_in_user = expected_username
            st.session_state.login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Log successful login
            logging.info(f"User {username} logged in successfully as {role}")
            st.rerun()
            # If remember me is checked, store in a more persistent way
            if remember_me:
                st.session_state.remember_login = True
            
            # Clear any previous login errors
            if "login_error" in st.session_state:
                del st.session_state.login_error
                
            return st.session_state.logged_in_user
        else:
            # Failed login
            show_login_error("Invalid role, username, or password")
            logging.warning(f"Failed login attempt for username: {username}, role: {role}")
            
            # Store the error in session state to persist across reruns
            st.session_state.login_error = "Invalid credentials"
            return None
    else:
        # Show any stored error messages
        if "login_error" in st.session_state:
            show_login_error(st.session_state.login_error)
        return None

##############################################
# Call Function: Handles Login and sets up Sidebar UI after login
##############################################
def call():
    user = simple_login()
    if not user:
        # Instead of halting execution, return False so the caller knows login didn't succeed.
        return False

    # Post-Login Sidebar UI: The sidebar.py will handle this part
    return True