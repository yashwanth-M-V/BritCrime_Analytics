#!/usr/bin/env python3
import streamlit as st
import pandas as pd
from utils.data_loader import load_data_from_azure, get_data_summary
from components.header import create_header

st.set_page_config(
    page_title="UK Crime Analytics",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def main():
    # Initialize session state for page navigation
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Overview"
    
    # Load data
    with st.spinner("🔄 Loading data from Azure Cloud..."):
        loaded_data = load_data_from_azure()

    if not loaded_data or loaded_data.get("crime_incidents", pd.DataFrame()).empty:
        st.error("❌ Failed to load data. Please check your Azure connection.")
        return

    # Create header and get filters (NO ARGUMENTS PASSED)
    filters = create_header()
    
    # Add spacing below fixed header
    st.markdown("<div style='margin-top: 280px;'></div>", unsafe_allow_html=True)

    # Page routing
    if st.session_state.current_page == "Overview":
        from pages import Overview
        Overview.render(loaded_data, filters)
        
    elif st.session_state.current_page == "Hotspots Map":
        from pages.2_hotspot&map import Hotspots_Map
        Hotspots_Map.render(loaded_data, filters)
        
    elif st.session_state.current_page == "Trends Analysis":
        from pages.3_trend&time_analysis import Trends_Analysis
        Trends_Analysis.render(loaded_data, filters)
        
    elif st.session_state.current_page == "Case Outcomes":
        from pages.4_case_outcome import Case_Outcomes
        Case_Outcomes.render(loaded_data, filters)
        
    elif st.session_state.current_page == "Incident Detail":
        from pages import Incident_Detail
        Incident_Detail.render(loaded_data, filters)

    # Optional Debug Summary
    with st.expander("📊 Data Summary"):
        summary = get_data_summary(loaded_data)
        for dataset, info in summary.items():
            st.write(f"**{dataset}**: {info['records']} records")
            if info['date_range']:
                st.write(f"  Date range: {min(info['date_range'])} → {max(info['date_range'])}")

if __name__ == "__main__":
    main()