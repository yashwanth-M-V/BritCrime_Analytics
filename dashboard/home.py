#!/usr/bin/env python3
"""
UK Crime Analytics Dashboard - Main Streamlit Application
"""

import streamlit as st
import pandas as pd
import base64
import os

from utils.sidebar import create_sidebar

# Page configuration (ONLY ONCE at the top)
st.set_page_config(
    page_title="UK Crime Analytics",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import components
from utils.data_loader import load_data_from_azure, get_data_summary
from components.kpi_cards import create_kpi_cards

# Function to convert image to base64 for embedding
def get_image_base64(image_path):
    """Convert image to base64 for HTML embedding"""
    try:
        if not os.path.exists(image_path):
            return None
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        return None

# Custom CSS for professional styling with fixed alignment
st.markdown("""
<style>
    /* Main header styling */
    .main-title {
        font-size: 3.5rem;
        color: #1f77b4;
        margin-bottom: 0;
        text-align: center;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        background: linear-gradient(135deg, #1f77b4 0%, #2ca02c 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.2;
    }
    
    .last-updated {
        text-align: center;
        color: #666;
        margin-top: 5px;
        margin-bottom: 0;
        font-size: 1.1rem;
        font-weight: 500;
    }
    
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        padding: 10px 0;
        gap: 20px;
    }
    
    .header-left, .header-right {
        flex: 0 0 auto;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .header-center {
        flex: 1;
        text-align: center;
        min-width: 0; /* Prevent flex item from overflowing */
    }
    
    .header-logo {
        width: 100px;
        height: 80px;
        object-fit: contain;
        transition: transform 0.3s ease;
    }
    
    .header-logo:hover {
        transform: scale(1.05);
    }
    
    .logo-placeholder {
        width: 100px;
        height: 80px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 10px;
        border: 2px dashed #1f77b4;
        color: #1f77b4;
        font-weight: bold;
        font-size: 0.9rem;
        text-align: center;
        padding: 5px;
    }
    
    .filter-section {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 20px;
        border-radius: 15px;
        margin: 20px 0;
        border: 1px solid #e9ecef;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #1f77b4;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        transition: transform 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    
    /* Footer styling - FIXED ALIGNMENT */
    .footer {
        background: linear-gradient(135deg, #1f77b4 0%, #2ca02c 100%);
        color: white;
        padding: 2rem;
        margin-top: 3rem;
        border-radius: 15px;
        box-shadow: 0 -4px 6px rgba(0,0,0,0.1);
    }
    
    .footer-content {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        flex-wrap: wrap;
        gap: 2rem;
    }
    
    .footer-left {
        flex: 1;
        min-width: 300px;
    }
    
    .footer-right {
        flex: 0 0 auto;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    
    .profile-image {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        border: 4px solid white;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        object-fit: cover;
    }
    
    .contact-info {
        margin-top: 1rem;
    }
    
    .contact-link {
        color: white;
        text-decoration: none;
        margin: 0.5rem 0;
        display: block;
        transition: color 0.3s ease;
        font-size: 1rem;
    }
    
    .contact-link:hover {
        color: #ffd700;
        text-decoration: underline;
    }
    
    .name {
        font-size: 1.8rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .title {
        font-size: 1.2rem;
        margin-bottom: 0.5rem;
        opacity: 0.9;
    }
    
    .education {
        font-size: 1rem;
        margin-bottom: 1rem;
        opacity: 0.8;
    }
    
    /* Streamlit component overrides */
    .stSelectbox, .stMultiselect {
        background-color: white;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Navigation button styling */
    .nav-button {
        background: linear-gradient(135deg, #1f77b4 0%, #2ca02c 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        font-size: 1rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .nav-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Ensure proper spacing */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

def create_header_with_images():
    """Create header with UK map on left and police logo on right - FIXED ALIGNMENT"""
    
    # Get images from the images folder
    uk_map_path = "images/uk_map.png"
    police_logo_path = "images/police_logo.png"
    
    # Convert images to base64
    uk_map_base64 = get_image_base64(uk_map_path)
    police_logo_base64 = get_image_base64(police_logo_path)
    
    # Create the header using a single markdown with proper flexbox
    header_html = """
    <div class="header-container">
        <div class="header-left">
    """
    
    # Left: UK Map
    if uk_map_base64:
        header_html += f'<img src="data:image/png;base64,{uk_map_base64}" class="header-logo" alt="UK Map">'
    else:
        header_html += '<div class="logo-placeholder">UK MAP</div>'
    
    header_html += """
        </div>
        <div class="header-center">
            <h1 class="main-title">UK CRIME ANALYTICS</h1>
            <p class="last-updated">Last Updated: 2025-10-20 | 91,518 Records Loaded</p>
        </div>
        <div class="header-right">
    """
    
    # Right: Police Logo
    if police_logo_base64:
        header_html += f'<img src="data:image/png;base64,{police_logo_base64}" class="header-logo" alt="Police Logo">'
    else:
        header_html += '<div class="logo-placeholder">POLICE</div>'
    
    header_html += """
        </div>
    </div>
    """
    
    st.markdown(header_html, unsafe_allow_html=True)

def create_footer():
    """Create professional footer with contact information and profile photo - FIXED ALIGNMENT"""
    
    # Get profile photo
    profile_photo_path = "images/yash_image.jpg"
    profile_photo_base64 = get_image_base64(profile_photo_path)
    
    footer_html = """
    <div class="footer">
        <div class="footer-content">
            <div class="footer-left">
                <div class="name">Madyala Venkata Yashwanth</div>
                <div class="title">Data Analyst / Engineer</div>
                <div class="education">M.Sc in Data Science and Big Data Engineering</div>
                <div class="contact-info">
                    <a href="mailto:madyalayashwanth@gmail.com" class="contact-link">📧 madyalayashwanth@gmail.com</a>
                    <a href="tel:+7706228928" class="contact-link">📱 +7706228928</a>
                    <a href="https://linkedin.com/in/madyalayashwanth" target="_blank" class="contact-link">💼 LinkedIn Profile</a>
                    <a href="https://github.com/yashwanth-M-V" target="_blank" class="contact-link">🐙 GitHub Profile</a>
                </div>
            </div>
            <div class="footer-right">
    """
    
    # Profile photo in footer
    if profile_photo_base64:
        footer_html += f'<img src="data:image/jpg;base64,{profile_photo_base64}" alt="Profile Photo" class="profile-image">'
    else:
        footer_html += '<img src="https://via.placeholder.com/120/1f77b4/ffffff?text=MY" alt="Profile Photo" class="profile-image">'
    
    footer_html += """
            </div>
        </div>
    </div>
    """
    
    st.markdown(footer_html, unsafe_allow_html=True)

def main():
    """
    Main Streamlit application
    """
    # HEADER WITH SPECIFIC IMAGES - FIXED ALIGNMENT
    create_header_with_images()
    
    # Display loading spinner while data loads
    with st.spinner("🔄 Loading crime data from Azure Cloud Storage..."):
        data = load_data_from_azure()
    
    # Check if data loaded successfully
    if not data or data.get('crime_incidents', pd.DataFrame()).empty:
        st.error("""
        ❌ Failed to load data. Please check:
        - Azure Storage connection string in .streamlit/secrets.toml
        - Internet connection
        - Data availability in Azure Blob Storage
        
        For local development, make sure you have a .streamlit/secrets.toml file with:
        AZURE_STORAGE_CONNECTION_STRING = "your_connection_string_here"
        """)
        
        # Show troubleshooting help
        with st.expander("🔧 Troubleshooting Help"):
            st.write("""
            1. **Create secrets file**: Create `.streamlit/secrets.toml` in your dashboard folder
            2. **Add connection string**: Get from Azure Portal → Storage Account → Access Keys
            3. **Restart app**: Save the file and restart the Streamlit app
            4. **Check internet**: Ensure your machine has internet access
            """)
        
        # Still show footer even if data fails
        create_footer()
        return
    
    # Create sidebar and get filters
    filters = create_sidebar()

    st.markdown("---")
    st.subheader("Dashboard Navigation")

    # Create 4 columns for the tiles
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("📊 Overview", use_container_width=True, key="nav_overview"):
            st.switch_page("pages/1_overview.py")
    
    with col2:
        if st.button("🗺️ Heatmap", use_container_width=True, key="nav_heatmap"):
            st.switch_page("pages/2_heatmap.py")
    
    with col3:
        if st.button("📈 Trend Analysis", use_container_width=True, key="nav_trend"):
            st.switch_page("pages/3_trend_time_analysis.py")
    
    with col4:
        if st.button("🛡️ Risk Assessment", use_container_width=True, key="nav_risk"):
            st.switch_page("pages/4_risk_assessment.py")

    # Create KPI cards
    create_kpi_cards(data, filters)
    
    # Data summary (collapsed by default)
    with st.expander("📊 Data Summary & Technical Details"):
        summary = get_data_summary(data)
        
        st.write("### Dataset Overview")
        for dataset, info in summary.items():
            if info['records'] > 0:
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.metric(f"{dataset}", f"{info['records']:,}")
                with col2:
                    if info['date_range']:
                        st.write(f"Date range: {min(info['date_range'])} to {max(info['date_range'])}")
        
        st.write("### About This Dashboard")
        st.write("""
        - **Data Source**: UK Police API (data.police.uk)
        - **Storage**: Azure Blob Storage
        - **Processing**: Python ETL Pipeline
        - **Visualization**: Streamlit + Plotly
        - **Deployment**: Streamlit Community Cloud
        """)

    # ADD FOOTER AT THE BOTTOM - FIXED ALIGNMENT
    create_footer()

if __name__ == "__main__":
    main()