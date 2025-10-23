# utils/sidebar.py
import streamlit as st
import pandas as pd
from utils.data_loader import load_data_from_azure

def create_sidebar():
    """Create sidebar with navigation and filters that appears on all pages"""
    
    # Load data for filter options
    data = load_data_from_azure(verbose=False)

    
    # Navigation Section
    st.sidebar.subheader("Dashboard Navigation")
    
    nav_col1, nav_col2 = st.sidebar.columns(2)
    
    with nav_col1:
        if st.button("📊 Overview", use_container_width=True, key="sidebar_overview"):
            st.switch_page("pages/1_overview.py")
    
    with nav_col2:
        if st.button("🗺️ Heatmap", use_container_width=True, key="sidebar_heatmap"):
            st.switch_page("pages/2_heatmap.py")
    
    nav_col3, nav_col4 = st.sidebar.columns(2)
    
    with nav_col3:
        if st.button("📈 Trend Analysis", use_container_width=True, key="sidebar_trend"):
            st.switch_page("pages/3_trend_time_analysis.py")
    
    with nav_col4:
        if st.button("🛡️ Risk Assessment", use_container_width=True, key="sidebar_risk"):
            st.switch_page("pages/4_risk_assessment.py")
    
    st.sidebar.markdown("---")
    
    # Filters Section
    st.sidebar.subheader("Data Filters")
    
    # Police Force Filter
    if not data.get('police_forces', pd.DataFrame()).empty:
        police_forces = data['police_forces']['force_name'].unique().tolist()
        selected_force = st.sidebar.selectbox(
            "Police Force", 
            options=["All Forces"] + police_forces,
            index=0
        )
    else:
        selected_force = "All Forces"
    
    # Time Period Filter
    if not data.get('crime_incidents', pd.DataFrame()).empty:
        time_periods = data['crime_incidents']['month'].unique().tolist()
        selected_period = st.sidebar.selectbox(
            "Time Period",
            options=["All Periods"] + sorted(time_periods),
            index=0
        )
    else:
        selected_period = "All Periods"
    
    # Crime Types Filter
    if not data.get('crime_incidents', pd.DataFrame()).empty:
        crime_types = data['crime_incidents']['category'].unique().tolist()
        selected_crimes = st.sidebar.multiselect(
            "Crime Types",
            options=crime_types,
            default=crime_types[:5] if crime_types else []
        )
    else:
        selected_crimes = []
    
    # Severity Level Filter
    if not data.get('crime_categories', pd.DataFrame()).empty and 'security_level' in data['crime_categories'].columns:
        severity_levels = data['crime_categories']['security_level'].unique().tolist()
        selected_severity = st.sidebar.multiselect(
            "Severity Level",
            options=severity_levels,
            default=severity_levels
        )
    else:
        selected_severity = []
    
    st.sidebar.markdown("---")
    st.sidebar.caption(f"Last Updated: 2025-10-20")
    
    # Return filters as dictionary
    return {
        'police_force': selected_force,
        'time_period': selected_period,
        'crime_types': selected_crimes,
        'severity_level': selected_severity
    }