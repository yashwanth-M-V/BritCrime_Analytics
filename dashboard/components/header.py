import streamlit as st
from datetime import datetime

def create_header():
    # --- CSS for professional styling and sticky header ---
    st.markdown("""
        <style>
            [data-testid="stSidebar"] {display: none;}
            [data-testid="stHeader"] {display: none;}
            
            /* Main container padding to account for fixed header */
            .main .block-container {
                padding-top: 0rem;
            }
            
            /* Sticky header container */
            .sticky-header {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                z-index: 999;
                background-color: white;
                padding: 15px 0px 5px 0px;
                box-shadow: 0 2px 12px rgba(0,0,0,0.1);
                border-bottom: 1px solid #e0e0e0;
            }
            
            /* Header container width matching Streamlit */
            .header-container {
                max-width: 100%;
                padding: 0 1rem;
            }
            
            /* Navigation tiles */
            .nav-tile {
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 12px 8px;
                margin: 4px 2px;
                background-color: #f8f9fa;
                transition: all 0.3s ease;
                text-decoration: none;
                color: #333;
                font-weight: 500;
                font-size: 0.85em;
                width: 100%;
                min-height: 70px;
                text-align: center;
                cursor: pointer;
            }
            
            .nav-tile:hover {
                background-color: #e9ecef;
                border-color: #495057;
                transform: translateY(-2px);
            }
            
            .nav-tile.active {
                background-color: #2c3e50;
                color: white;
                border-color: #2c3e50;
                font-weight: 600;
            }
            
            .tile-icon {
                font-size: 20px;
                margin-bottom: 4px;
            }
            
            .tile-title {
                font-size: 0.75em;
                font-weight: 500;
                margin: 0;
            }
            
            .tile-page {
                font-size: 0.7em;
                color: #666;
                margin-top: 2px;
                margin: 0;
            }
            
            .nav-tile.active .tile-page {
                color: #e0e0e0;
            }
            
            /* UK Map and Police symbol containers */
            .symbol-container {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                background-color: #f8f9fa;
                padding: 15px 10px;
                text-align: center;
                height: 100px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
            }
            
            .symbol-icon {
                font-size: 32px;
                margin-bottom: 8px;
            }
            
            .symbol-label {
                font-size: 0.8em;
                color: #666;
                font-weight: 500;
            }
            
            /* Main title styling */
            .main-title {
                text-align: center;
                color: #2c3e50;
                font-weight: 700;
                font-size: 2.2em;
                margin: 0;
                padding: 0;
            }
            
            .last-updated {
                text-align: center;
                color: #7f8c8d;
                font-size: 0.85em;
                margin: 0;
                padding: 0;
            }
            
            /* Filter section */
            .filter-section {
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 15px;
                margin: 10px 0;
                border: 1px solid #e0e0e0;
            }
            
            .filter-title {
                color: #2c3e50;
                font-weight: 600;
                margin-bottom: 12px;
                font-size: 1em;
            }
            
            /* Custom button styling to look like tiles */
            .nav-button-container {
                width: 100%;
            }
            
            .nav-button-container button {
                width: 100%;
                height: 80px;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                background-color: #f8f9fa;
                transition: all 0.3s ease;
            }
            
            .nav-button-container button:hover {
                background-color: #e9ecef;
                border-color: #495057;
                transform: translateY(-2px);
            }
            
            .nav-button-container button[data-active="true"] {
                background-color: #2c3e50;
                color: white;
                border-color: #2c3e50;
            }
        </style>
    """, unsafe_allow_html=True)

    # --- Start Sticky Header Container ---
    st.markdown("<div class='sticky-header'>", unsafe_allow_html=True)
    st.markdown("<div class='header-container'>", unsafe_allow_html=True)

    # --- HEADER ROW: UK Map - Title - Police Symbol ---
    col1, col2, col3 = st.columns([2, 6, 2])

    with col1:
        st.markdown("""
        <div class='symbol-container'>
            <div class='symbol-icon'>🗺️</div>
            <div class='symbol-label'>UK Map</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("<h1 class='main-title'>UK CRIME ANALYTICS</h1>", unsafe_allow_html=True)
        st.markdown(f"<p class='last-updated'>Last Updated: {datetime.now().strftime('%d %B %Y')}</p>", 
                    unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class='symbol-container'>
            <div class='symbol-icon'>👮</div>
            <div class='symbol-label'>Police Symbol</div>
        </div>
        """, unsafe_allow_html=True)

    # --- NAVIGATION TILES (5 pages) ---
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Define navigation items
    nav_items = [
        {"id": "Overview", "icon": "📊", "title": "Overview", "page": "Page 1"},
        {"id": "Hotspots Map", "icon": "📍", "title": "Hotspots Map", "page": "Page 2"},
        {"id": "Trends Analysis", "icon": "📈", "title": "Trends Analysis", "page": "Page 3"},
        {"id": "Case Outcomes", "icon": "⚖️", "title": "Case Outcomes", "page": "Page 4"},
        {"id": "Incident Detail", "icon": "🔍", "title": "Incident Detail", "page": "Page 5"}
    ]
    
    # Create tiles using columns
    cols = st.columns(5)
    for i, item in enumerate(nav_items):
        with cols[i]:
            is_active = st.session_state.current_page == item["id"]
            
            # Create custom button with HTML styling
            button_html = f"""
            <div class="nav-button-container">
                <button data-active="{str(is_active).lower()}" onclick="window.navigateToPage('{item['id']}')">
                    <div style="font-size: 20px; margin-bottom: 4px;">{item['icon']}</div>
                    <div style="font-size: 0.75em; font-weight: 500;">{item['title']}</div>
                    <div style="font-size: 0.7em; color: {'#e0e0e0' if is_active else '#666'};">{item['page']}</div>
                </button>
            </div>
            """
            st.markdown(button_html, unsafe_allow_html=True)
            
            # Add JavaScript for navigation
            st.markdown(f"""
            <script>
            window.navigateToPage = function(pageId) {{
                // This will trigger a Streamlit rerun with the new page
                const event = new CustomEvent('navigate', {{ detail: {{ page: pageId }} }});
                document.dispatchEvent(event);
            }}
            
            // Handle navigation events
            document.addEventListener('navigate', function(e) {{
                // This would typically update Streamlit session state
                // For now, we'll use a workaround with query parameters
                window.location.href = `?page=${{e.detail.page}}`;
            }});
            </script>
            """, unsafe_allow_html=True)
            
            # Streamlit button as fallback (hidden but functional)
            if st.button(
                f"Navigate to {item['title']}",
                key=f"nav_{item['id']}",
                use_container_width=True,
                type="secondary"
            ):
                st.session_state.current_page = item["id"]
                st.rerun()

    # --- FILTERS SECTION ---
    st.markdown("<div class='filter-section'>", unsafe_allow_html=True)
    st.markdown("<div class='filter-title'>🔍 Data Filters</div>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        police_force = st.selectbox(
            "Police Force", 
            ["All Forces", "Metropolitan", "West Yorkshire", "Greater Manchester"],
            key="header_police"
        )
    with col2:
        month = st.selectbox(
            "Month", 
            ["All", "January", "February", "March", "April", "May", "June"],
            key="header_month"
        )
    with col3:
        crime_type = st.selectbox(
            "Crime Type", 
            ["All Types", "Violence", "Burglary", "Fraud", "Theft", "Robbery"],
            key="header_crime"
        )
    with col4:
        severity = st.selectbox(
            "Severity Level", 
            ["All Levels", "Low", "Medium", "High", "Critical"],
            key="header_severity"
        )
    
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)  # Close header-container
    st.markdown("</div>", unsafe_allow_html=True)  # Close sticky-header

    # Return filter values
    return {
        "police_force": police_force,
        "month": month,
        "crime_type": crime_type,
        "severity": severity
    }