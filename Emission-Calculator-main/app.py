import streamlit as st
from streamlit_option_menu import option_menu
from app_pages.overview import overview_page
from app_pages.Login import simple_login
from app_pages.sidebar import render_sidebar
from visualizations.OverallAnalysis import vis
from common import create_database
from app_pages.Explain import explain_page
import requests
import streamlit.components.v1 as components
from datetime import datetime
import time
st.set_page_config(layout="wide")
# Try to import optional components with fallbacks
try:
    from streamlit_lottie import st_lottie
    LOTTIE_AVAILABLE = True
except ImportError:
    LOTTIE_AVAILABLE = False

try:
    from streamlit_card import card
    CARD_AVAILABLE = True
except ImportError:
    CARD_AVAILABLE = False

# Custom CSS with enhanced styling, animations and glassmorphism effects
st.markdown("""
<style>
    /* Base Theme */
    .stApp {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        color: #f8f9fa;
    }
 
    .main .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }
    
    /* Typography Enhancement */
    h1 {
        color: #ffffff;
        font-size: 2.8rem;
        font-weight: 800;
        text-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        letter-spacing: -0.5px;
        margin-bottom: 1.5rem;
        background: linear-gradient(90deg, #ffffff, #4e8cff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    h2 {
        color: #e0e0e0;
        font-size: 2rem;
        font-weight: 700;
        margin-top: 2rem;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }
    
    h3 {
        color: #c8d6e5;
        font-size: 1.5rem;
        font-weight: 600;
        margin-top: 1.5rem;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    /* Card Styling with Glassmorphism */
    .css-1r6slb0, .css-keje6w {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(10px) !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1) !important;
        padding: 20px !important;
        margin-bottom: 20px !important;
        transition: transform 0.3s ease, box-shadow 0.3s ease !important;
    }
    
    .css-1r6slb0:hover, .css-keje6w:hover {
        transform: translateY(-5px) !important;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15) !important;
    }
    
    /* Custom Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #4e8cff, #367bd8);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(78, 140, 255, 0.3);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(78, 140, 255, 0.4);
        background: linear-gradient(90deg, #367bd8, #2563eb);
    }
    
    .stButton>button:active {
        transform: translateY(1px);
    }
    
    /* Enhanced Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: rgba(0, 0, 0, 0.2);
        border-radius: 10px;
        padding: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(43, 43, 43, 0.7);
        border-radius: 8px;
        padding: 10px 20px;
        color: white;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #4e8cff, #367bd8) !important;
        transform: scale(1.05);
        box-shadow: 0 4px 12px rgba(78, 140, 255, 0.3);
    }
    
    /* Sliders and Inputs */
    .stSlider > div {
        padding-top: 0.7rem;
    }
    
    .stSlider [data-baseweb="slider"] {
        height: 6px;
    }
    
    .stSlider [data-baseweb="thumb"] {
        background-color: #4e8cff;
        height: 18px;
        width: 18px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        transform: translate(-50%, -50%);
    }
    
    /* Progress Bar */
    .stProgress > div > div {
        background-color: rgba(255, 255, 255, 0.14);
        height: 10px;
        border-radius: 10px;
    }
    
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #4cc9f0, #4361ee);
    }
    
    /* Metrics */
    .css-1wivap2, [data-testid="stMetricValue"] {
        background: linear-gradient(90deg, #3A86FF, #4361EE);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem !important;
        font-weight: 700 !important;
    }
    
    /* Animated Elements */
    @keyframes fadeInDown {
      from { opacity: 0; transform: translateY(-20px); }
      to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes fadeInUp {
      from { opacity: 0; transform: translateY(20px); }
      to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes float {
      0% { transform: translateY(0px); }
      50% { transform: translateY(-10px); }
      100% { transform: translateY(0px); }
    }
    
    @keyframes pulse {
      0% { transform: scale(1); }
      50% { transform: scale(1.05); }
      100% { transform: scale(1); }
    }
    
    /* Hero Section */
    .hero-section {
        background-image: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)), url('https://source.unsplash.com/1600x900/?climate,nature');
        background-size: cover;
        background-position: center;
        padding: 120px 20px;
        text-align: center;
        color: #ffffff;
        min-height: 80vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
        position: relative;
        overflow: hidden;
        border-radius: 16px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
    }
    
    .hero-title {
        font-size: 3.8rem;
        font-weight: bold;
        text-shadow: 2px 2px 8px #000;
        animation: fadeInDown 1.2s ease-in-out;
        margin-bottom: 1rem;
    }
    
    .hero-subtitle {
        font-size: 1.7rem;
        margin-top: 10px;
        animation: fadeInUp 1.2s ease-in-out;
        text-shadow: 1px 1px 6px #000;
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
        line-height: 1.5;
    }
    
    .cta-button {
        margin-top: 40px;
        background: linear-gradient(90deg, #4e8cff, #367bd8);
        color: #fff;
        padding: 18px 36px;
        border: none;
        border-radius: 50px;
        font-size: 1.4rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 8px 20px rgba(78, 140, 255, 0.4);
        animation: pulse 2s infinite ease-in-out;
    }
    
    .cta-button:hover {
        background: linear-gradient(90deg, #367bd8, #2563eb);
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(78, 140, 255, 0.5);
    }
    
    .widget-container {
        background: rgba(0, 0, 0, 0.3);
        padding: 30px;
        border-radius: 16px;
        margin-top: 30px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(12px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
        animation: fadeInUp 1s ease-in-out 0.5s;
        animation-fill-mode: both;
    }
    
    /* Glass Card Styling */
    .glass-card {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 48px rgba(0, 0, 0, 0.2);
    }
    
    /* Floating element animation */
    .floating {
        animation: float 6s ease-in-out infinite;
    }
    
    /* Dashboard Card Styling */
    .dashboard-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
    }
    
    .dashboard-card:hover {
        transform: translateY(-5px);
    }
    
    /* Info Box Styling */
    .stAlert {
        background: rgba(74, 222, 128, 0.1) !important;
        border: 1px solid rgba(74, 222, 128, 0.3) !important;
        color: #e0e0e0 !important;
        border-radius: 8px !important;
        backdrop-filter: blur(4px) !important;
    }
    
    /* Mobile Responsiveness */
    @media only screen and (max-width: 768px) {
        .hero-title { font-size: 2.5rem; }
        .hero-subtitle { font-size: 1.2rem; }
        .cta-button { padding: 12px 24px; font-size: 1.1rem; }
        h1 { font-size: 2rem; }
        h2 { font-size: 1.6rem; }
        h3 { font-size: 1.3rem; }
    }
</style>
""", unsafe_allow_html=True)

# Initialize database
try:
    create_database()
except Exception as e:
    st.error(f"Failed to initialize database: {e}")
    st.stop()

# ------------------------------
# Enhanced Lottie animation loader with caching
@st.cache_data(ttl=3600)
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None

# ------------------------------
# Particle.js Background Animation
def render_particle_background():
    particle_html = """
    <div id="particles-js" style="position:fixed; width:100%; height:100%; top:0; left:0; z-index:-1;"></div>
    <script src="https://cdn.jsdelivr.net/particles.js/2.0.0/particles.min.js"></script>
    <script>
      document.addEventListener("DOMContentLoaded", function() {
        particlesJS("particles-js", {
          "particles": {
            "number": {
              "value": 80,
              "density": {
                "enable": true,
                "value_area": 800
              }
            },
            "color": {
              "value": "#ffffff"
            },
            "shape": {
              "type": "circle",
              "stroke": {
                "width": 0,
                "color": "#000000"
              },
              "polygon": {
                "nb_sides": 5
              }
            },
            "opacity": {
              "value": 0.4,
              "random": true,
              "anim": {
                "enable": true,
                "speed": 0.3,
                "opacity_min": 0.1,
                "sync": false
              }
            },
            "size": {
              "value": 3,
              "random": true,
              "anim": {
                "enable": true,
                "speed": 2,
                "size_min": 0.1,
                "sync": false
              }
            },
            "line_linked": {
              "enable": true,
              "distance": 150,
              "color": "#4e8cff",
              "opacity": 0.2,
              "width": 1
            },
            "move": {
              "enable": true,
              "speed": 1,
              "direction": "none",
              "random": true,
              "straight": false,
              "out_mode": "out",
              "bounce": false,
              "attract": {
                "enable": false,
                "rotateX": 600,
                "rotateY": 1200
              }
            }
          },
          "interactivity": {
            "detect_on": "canvas",
            "events": {
              "onhover": {
                "enable": true,
                "mode": "grab"
              },
              "onclick": {
                "enable": true,
                "mode": "push"
              },
              "resize": true
            },
            "modes": {
              "grab": {
                "distance": 140,
                "line_linked": {
                  "opacity": 0.5
                }
              },
              "push": {
                "particles_nb": 4
              }
            }
          },
          "retina_detect": true
        });
      });
    </script>
    """
    components.html(particle_html, height=0)

# ------------------------------
# Function to render animated counter
def render_animated_counter(label, value, prefix="", suffix=""):
    counter_html = f"""
    <div class="animated-counter" style="text-align: center; margin: 20px 0;">
        <h3 style="margin-bottom: 10px;">{label}</h3>
        <div class="counter-value" style="font-size: 3rem; font-weight: bold; color: #4e8cff;"
             data-target="{value}" id="counter-{label.replace(' ', '-')}">0</div>
        <div style="font-size: 1.2rem; color: #c8d6e5;">{prefix} {suffix}</div>
    </div>
    
    <script>
        document.addEventListener("DOMContentLoaded", function() {{
            const counters = document.querySelectorAll('.counter-value');
            
            counters.forEach(counter => {{
                const target = +counter.getAttribute('data-target');
                const increment = target / 100;
                
                const updateCounter = () => {{
                    const value = +counter.innerText;
                    if (value < target) {{
                        counter.innerText = (value + increment).toFixed(2);
                        setTimeout(updateCounter, 20);
                    }} else {{
                        counter.innerText = target.toFixed(2);
                    }}
                }};
                
                setTimeout(updateCounter, 400);
            }});
        }});
    </script>
    """
    components.html(counter_html, height=150)

# ------------------------------
# Enhanced landing page with interactive elements
def render_landing_page():
    # Render particle animation in the background
    render_particle_background()
    
  # Enhanced Hero section with typwriter animation
    st.markdown(f"""
        <div class="hero-section">
            <div class="hero-title">Carbon Emission Dashboard</div>
            <div class="hero-subtitle">Calculate, analyze, and reduce your event's carbon footprint with our interactive AI-powered tools</div>
            <button type="button" class="cta-button" id="login-btn">Understand Emissions</button>
            
        </div>
                
        <script>
            document.addEventListener("DOMContentLoaded", function() {{
                const btn = document.getElementById("login-btn");
                if(btn) {{
                    btn.addEventListener("click", function() {{
                        const sidebar = window.parent.document.querySelector('[data-testid="stSidebar"]');
                        if(sidebar) {{
                            sidebar.scrollIntoView({{ behavior: 'smooth' }});
                            sidebar.style.animation = "pulse 1s 3";
                        }}
                    }});
                }}
                
                // Add typewriter effect to subtitle
                const subtitle = document.querySelector(".hero-subtitle");
                const text = subtitle.textContent;
                subtitle.textContent = "";
                
                let i = 0;
                function typeWriter() {{
                    if (i < text.length) {{
                        subtitle.textContent += text.charAt(i);
                        i++;
                        setTimeout(typeWriter, 30);
                    }}
                }}
                
                setTimeout(typeWriter, 1000);
            }});
        </script>
    """, unsafe_allow_html=True)
    
    # Features showcase with animation
    st.markdown("""
    <div style="margin-top: 40px; animation: fadeInUp 1s ease-in-out;">
        <h2 style="text-align: center; margin-bottom: 30px;">Key Features</h2>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
            <div class="glass-card">
                <div style="text-align: center; font-size: 2rem; margin-bottom: 15px; color: #4e8cff;">📊</div>
                <h3 style="text-align: center; margin-bottom: 10px;">Real-time Analytics</h3>
                <p style="text-align: center; color: #c8d6e5;">Monitor your carbon footprint with interactive charts and visualizations.</p>
            </div>
            <div class="glass-card">
                <div style="text-align: center; font-size: 2rem; margin-bottom: 15px; color: #4e8cff;">🌿</div>
                <h3 style="text-align: center; margin-bottom: 10px;">Sustainability Insights</h3>
                <p style="text-align: center; color: #c8d6e5;">Get personalized recommendations to reduce your environmental impact.</p>
            </div>
            <div class="glass-card">
                <div style="text-align: center; font-size: 2rem; margin-bottom: 15px; color: #4e8cff;">📱</div>
                <h3 style="text-align: center; margin-bottom: 10px;">Mobile Friendly</h3>
                <p style="text-align: center; color: #c8d6e5;">Access your dashboard on any device, anywhere, anytime.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True) 
    # Video demonstration with enhanced styling
    st.markdown('<h2 style="text-align: center; margin: 40px 0 20px;">Climate Impact Preview</h2>', unsafe_allow_html=True)
    st.components.v1.html("""
        <div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; border-radius: 12px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);">
            <iframe style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;" 
            src="https://www.youtube.com/embed/-gejkWj3K24?autoplay=0&mute=0&loop=0&controls=1" 
            frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
            allowfullscreen title="Climate Change Impact Visualization"></iframe>
        </div>
    """, height=400)
    
    # Accessibility note with enhanced styling
    st.markdown('<p style="text-align: center; font-style: italic; color: #c8d6e5; margin-top: 10px;">Video: Understanding carbon emissions and climate change impacts</p>', unsafe_allow_html=True)
    
    # Animated Stats Counter
    st.markdown('<h2 style="text-align: center; margin: 40px 0 20px;">Impact Statistics</h2>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        render_animated_counter("Users Worldwide", 10567, suffix="active users")
    
    with col2:
        render_animated_counter("CO₂ Saved", 5280.75, suffix="tons")
    
    with col3:
        render_animated_counter("Events Analyzed", 3245, "")
    
    # "Did you know?" facts with animated carousel
    facts = [
        "Transportation contributes about 14% of global greenhouse gas emissions.",
        "Electricity and heat production are the largest contributors to global CO₂ emissions.",
        "Sustainable practices can reduce your event's carbon footprint by up to 30%.",
        "Small changes in energy use can lead to big environmental benefits over time.",
        "Virtual events can reduce carbon footprints by up to 94% compared to in-person events.",
        "LED lighting uses up to 80% less energy than traditional lighting at events."
    ]
    
    fact_index = int(time.time()) % len(facts)  # Changes fact every second
    fact = facts[fact_index]
    
    st.markdown(f"""
    <div class="glass-card" style="margin-top: 20px;">
        <h3 style="text-align: center; margin-bottom: 15px;">Did You Know?</h3>
        <p style="text-align: center; font-size: 1.1rem; color: #e0e0e0;">{fact}</p>
        <div style="text-align: center; margin-top: 15px;">
            <div style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background-color: {fact_index == 0 and '#4e8cff' or 'rgba(255,255,255,0.3)'}; margin: 0 5px;"></div>
            <div style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background-color: {fact_index == 1 and '#4e8cff' or 'rgba(255,255,255,0.3)'}; margin: 0 5px;"></div>
            <div style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background-color: {fact_index == 2 and '#4e8cff' or 'rgba(255,255,255,0.3)'}; margin: 0 5px;"></div>
            <div style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background-color: {fact_index == 3 and '#4e8cff' or 'rgba(255,255,255,0.3)'}; margin: 0 5px;"></div>
            <div style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background-color: {fact_index == 4 and '#4e8cff' or 'rgba(255,255,255,0.3)'}; margin: 0 5px;"></div>
            <div style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background-color: {fact_index == 5 and '#4e8cff' or 'rgba(255,255,255,0.3)'}; margin: 0 5px;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Progress display with tooltip
    st.markdown(f"""
    <div style="position: relative; margin-top: 15px; padding: 15px; background: rgba(78, 140, 255, 0.1); border-radius: 8px; border-left: 4px solid #4e8cff;">
        <p style="margin: 0; color: #e0e0e0;">Working together, we can reach our emission reduction goals. Join 10,000+ other organizations making a difference.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Call to action cards
    st.markdown('<h2 style="text-align: center; margin: 40px 0 20px;">Get Started Today</h2>', unsafe_allow_html=True)
    
    # Enhanced card design using columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="glass-card" style="text-align: center; height: 100%;">
            <div style="font-size: 2.5rem; margin-bottom: 15px; color: #4e8cff;">🔍</div>
            <h3>Analyze</h3>
            <p style="color: #c8d6e5;">Get detailed insights into your carbon footprint across all emission scopes.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="glass-card" style="text-align: center; height: 100%; transform: translateY(-10px); box-shadow: 0 12px 40px rgba(78, 140, 255, 0.2);">
            <div style="font-size: 2.5rem; margin-bottom: 15px; color: #4e8cff;">📊</div>
            <h3>Visualize</h3>
            <p style="color: #c8d6e5;">Interactive charts and dashboards to track your progress over time.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="glass-card" style="text-align: center; height: 100%;">
            <div style="font-size: 2.5rem; margin-bottom: 15px; color: #4e8cff;">🌱</div>
            <h3>Improve</h3>
            <p style="color: #c8d6e5;">Actionable recommendations to reduce your environmental impact.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Testimonials with modern carousel effect
    st.markdown('<h2 style="text-align: center; margin: 40px 0 20px;">What Users Say</h2>', unsafe_allow_html=True)
    
    testimonials = [
        {"name": "Sarah Johnson", "role": "Event Manager", "text": "This dashboard transformed how we plan sustainable events. We've reduced our carbon footprint by 40% in just six months."},
        {"name": "Michael Chen", "role": "Sustainability Director", "text": "The interactive visualizations make it easy to identify areas for improvement. Our stakeholders are impressed with the detailed reports."},
        {"name": "Emma Rodriguez", "role": "Conference Organizer", "text": "I love how intuitive the interface is. Even team members with no technical background can understand our environmental impact."}
    ]
    
    # Create testimonial carousel
    testimonial_html = """
    <div class="testimonial-container" style="position: relative; padding: 20px 40px;">
        <div class="testimonial-track" style="display: flex; overflow-x: hidden;">
    """
    
    for idx, testimonial in enumerate(testimonials):
        testimonial_html += f"""
        <div class="testimonial-card" id="testimonial-{idx}" style="min-width: 100%; background: rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 30px; margin-right: 20px; border: 1px solid rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px);">
            <div style="font-size: 1.8rem; color: #4e8cff; margin-bottom: 15px;">❝</div>
            <p style="font-style: italic; color: #e0e0e0; font-size: 1.1rem; margin-bottom: 20px;">{testimonial['text']}</p>
            <div style="display: flex; align-items: center;">
                <div style="width: 50px; height: 50px; border-radius: 50%; background-color: #4e8cff; display: flex; align-items: center; justify-content: center; font-weight: bold; color: white; font-size: 1.2rem;">{testimonial['name'][0]}</div>
                <div style="margin-left: 15px;">
                    <p style="margin: 0; font-weight: bold; color: white;">{testimonial['name']}</p>
                    <p style="margin: 0; font-size: 0.9rem; color: #c8d6e5;">{testimonial['role']}</p>
                </div>
            </div>
        </div>
        """
    
    testimonial_html += """
        </div>
        <div style="text-align: center; margin-top: 20px;">
    """
    
    for i in range(len(testimonials)):
        testimonial_html += f"""
        <span class="dot" onclick="currentTestimonial({i})" style="display: inline-block; width: 12px; height: 12px; border-radius: 50%; background-color: rgba(255, 255, 255, 0.3); margin: 0 5px; cursor: pointer; transition: background-color 0.3s ease;"></span>
        """
    
    testimonial_html += """
        </div>
    </div>
    
    <script>
        // Auto-rotating testimonials
        let testimonialIndex = 0;
        const dots = document.querySelectorAll('.dot');
        const cards = document.querySelectorAll('.testimonial-card');
        const track = document.querySelector('.testimonial-track');
        
        function showTestimonial(n) {
            testimonialIndex = n;
            
            // Update dots
            for (let i = 0; i < dots.length; i++) {
                dots[i].style.backgroundColor = i === testimonialIndex ? '#4e8cff' : 'rgba(255, 255, 255, 0.3)';
            }
            
            // Slide to the correct testimonial
            if (track) {
                track.style.transition = 'transform 0.5s ease';
                track.style.transform = `translateX(-${testimonialIndex * 100}%)`;
            }
        }
        
        function currentTestimonial(n) {
            showTestimonial(n);
        }
        
        function nextTestimonial() {
            testimonialIndex = (testimonialIndex + 1) % dots.length;
            showTestimonial(testimonialIndex);
        }
        
        // Start the auto-rotation
        setInterval(nextTestimonial, 5000);
        
        // Initialize
        showTestimonial(0);
    </script>
    """
    
    components.html(testimonial_html, height=300)
    
    # FAQ section with accordion
    st.markdown('<h2 style="text-align: center; margin: 40px 0 20px;">Frequently Asked Questions</h2>', unsafe_allow_html=True)
    
    faq_items = [
        {"question": "What are Scope 1, 2, and 3 emissions?", 
         "answer": "Scope 1 emissions are direct emissions from owned or controlled sources. Scope 2 covers indirect emissions from purchased electricity, steam, heating, and cooling. Scope 3 includes all other indirect emissions in a company's value chain."},
        {"question": "How accurate is the carbon footprint calculator?", 
         "answer": "Our calculator uses industry-standard emission factors and methodologies aligned with the Greenhouse Gas Protocol. The accuracy depends on the quality of input data, typically providing estimates within 5-10% of actual emissions."},
        {"question": "Can I export reports for sustainability reporting?", 
         "answer": "Yes, all dashboard data can be exported in multiple formats (PDF, CSV, Excel) compatible with major sustainability reporting frameworks like GRI, CDP, and TCFD."},
        {"question": "How often should I update my emission data?", 
         "answer": "For optimal tracking, we recommend monthly updates for operational emissions (Scope 1 & 2) and quarterly updates for value chain emissions (Scope 3)."}
    ]
    
    for i, faq in enumerate(faq_items):
        with st.expander(faq["question"]):
            st.markdown(f"<p style='color: #e0e0e0;'>{faq['answer']}</p>", unsafe_allow_html=True)

    # Footer with newsletter signup
    st.markdown("""
    <div style="margin-top: 60px; padding: 40px 20px; background: rgba(0, 0, 0, 0.2); border-radius: 12px; text-align: center;">
        <h2 style="margin-bottom: 20px;">Stay Updated</h2>
        <p style="max-width: 600px; margin: 0 auto 20px; color: #c8d6e5;">Subscribe to our newsletter for the latest sustainability tips, feature updates, and climate action news.</p>
        <div style="max-width: 500px; margin: 0 auto; display: flex; gap: 10px;">
            <input type="email" placeholder="Your email address" style="flex: 1; padding: 12px 15px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.2); background: rgba(0, 0, 0, 0.2); color: white; outline: none;">
            <button style="background: linear-gradient(90deg, #4e8cff, #367bd8); color: white; border: none; border-radius: 8px; padding: 12px 20px; font-weight: 600; cursor: pointer;">Subscribe</button>
        </div>
        <p style="font-size: 0.8rem; margin-top: 15px; color: #a0a0a0;">By subscribing, you agree to our Privacy Policy and Terms of Service</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Add subtle attribution
    st.markdown("""
    <div style="text-align: center; margin-top: 30px; padding: 20px; font-size: 0.8rem; color: rgba(255, 255, 255, 0.5);">
        © 2025 Carbon Emission Dashboard | Designed with 💚 for a sustainable future
    </div>
    """, unsafe_allow_html=True)

# ------------------------------
# Function to handle login with enhanced visualization
def handle_authentication():
    # Add visual enhancements to the login process
    st.markdown("""
    <div style="position: fixed; top: 0; right: 0; padding: 20px; z-index: 1000;">
        <div class="glass-card" style="display: inline-block; padding: 10px 15px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 10px; height: 10px; border-radius: 50%; background: #4dfa9c;"></div>
                <span style="color: #e0e0e0; font-size: 0.9rem;">System Online</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    user = simple_login()
    if not user:
        return False

# ------------------------------
# Enhanced dashboard layout with interactive elements
def render_dashboard():
    # Add a top navigation bar with user info and quick actions
    user = st.session_state.logged_in_user
    
    # Current date and time for dynamic display
    current_date = datetime.now().strftime("%B %d, %Y")
    
    # Top navigation bar with user info
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; color: #EDF0FF;">
        <div>
            <h1>Emission Calculator & Analysis Dashboard</h1>
            <p style="color: #c8d6e5;">{current_date}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Dashboard description with animated border
    st.markdown("""
    <div style="padding: 20px; border-radius: 12px; margin-bottom: 30px; background: rgba(78, 140, 255, 0.05); position: relative; overflow: hidden;">
        <div style="position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, transparent, #4e8cff, transparent); animation: border-flow 3s infinite linear;"></div>
        <p style="color: #e0e0e0; margin: 0;">This dashboard is designed to calculate and analyze emissions for Scope 1, Scope 2, and Scope 3. Use the navigation below to access different sections of the tool.</p>
    </div>
    <style>
        @keyframes border-flow {
            0% { background-position: -300px 0; }
            100% { background-position: 300px 0; }
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Enhanced option menu with icons and animations
    selected = option_menu(
        menu_title="Emissions Calculators",
        menu_icon="cloud-fill",
        options=["Overview", "Analysis", "Reports"],
        icons=["house-fill", "graph-up-arrow", "file-earmark-text"],
        orientation="horizontal",
        styles={
            "container": {"padding": "5px", "background-color": "rgba(0, 0, 0, 0.2)", "border-radius": "10px"},
            "icon": {"color": "#4e8cff", "font-size": "18px"},
            "nav-link": {"font-size": "16px", "text-align": "center", "margin": "0px", "padding": "10px 20px", 
                         "border-radius": "8px", "transition": "all 0.3s ease"},
            "nav-link-selected": {"background": "linear-gradient(90deg, #4e8cff, #367bd8)",
                                 "color": "white", "font-weight": "600"}
        }
    )
    
    # Add a visual loading effect
    with st.spinner(f"Loading {selected}..."):
        time.sleep(0.5)  # Brief loading animation for enhanced UX
        
        # Map options to pages
        pages = {
            "Overview": overview_page,
            "Analysis": vis
        }
        
        # Render the selected page with additional styling
        if selected in pages:
            pages[selected]()
        elif selected == "Reports":
            st.markdown('<h2 style="margin-bottom: 20px;">Reports Dashboard</h2>', unsafe_allow_html=True)
            st.info("Reports module is loading. This feature will be available in the next update.")
            
            # Placeholder report cards
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("""
                <div class="dashboard-card">
                    <h3>Monthly Emissions Report</h3>
                    <div style="color: #c8d6e5; margin-bottom: 15px;">Last generated: March 28, 2025</div>
                    <button style="background: linear-gradient(90deg, #4e8cff, #367bd8); color: white; border: none; border-radius: 8px; padding: 8px 16px; cursor: pointer;">Generate Report</button>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="dashboard-card">
                    <h3>Quarterly Sustainability Analysis</h3>
                    <div style="color: #c8d6e5; margin-bottom: 15px;">Last generated: Q1 2025</div>
                    <button style="background: linear-gradient(90deg, #4e8cff, #367bd8); color: white; border: none; border-radius: 8px; padding: 8px 16px; cursor: pointer;">Generate Report</button>
                </div>
                """, unsafe_allow_html=True)

# ------------------------------
# Main application flow with enhanced visuals
if "logged_in_user" in st.session_state:
    if "sidebar_page" not in st.session_state:
        st.session_state.sidebar_page = "main"
    render_sidebar(st.session_state.logged_in_user)
    if st.session_state.get("sidebar_page", "main") == "main":
        # Render the enhanced dashboard interface
        render_particle_background()  # Add particle background for logged-in state too
        render_dashboard()
else:
    # Render the enhanced pre-login landing page with interactive elements
    render_landing_page()
    if handle_authentication():
        st.rerun()
    else:
        st.stop()
