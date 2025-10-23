#!/usr/bin/env python3
"""
Header Component - Professional header with inline filters
"""

import streamlit as st
import pandas as pd
from datetime import datetime

def create_header(loaded_data):
    """
    Create professional header with inline filters
    """
    # Header with logo placeholders and title
    col_logo_left, col_title, col_logo_right = st.columns([1, 3, 1])
    
    with col_logo_left:
        # UK Flag placeholder
        st.markdown(
            """
            <div class="logo-placeholder">
                <div style='font-size: 32px; margin-bottom: 5px;'>🇬🇧</div>
                <div style='font-size: 12px; color: #666;'>UK Flag</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with col_title:
        # Main title
        st.markdown(
            """
            <h1 class="main-title">UK CRIME ANALYTICS</h1>
            """, 
            unsafe_allow_html=True
        )
        
        # Last updated information
        display_date = get_last_updated_date(loaded_data)
        st.markdown(
            f"""
            <p class="last-updated">
                📅 Last Updated: {display_date} | 
                📊 {get_total_records(loaded_data):,} Records Loaded
            </p>
            """, 
            unsafe_allow_html=True
        )
    
    with col_logo_right:
        # Police logo placeholder
        st.markdown(
            """
            <div class="logo-placeholder">
                <div style='font-size: 32px; margin-bottom: 5px;'>👮</div>
                <div style='font-size: 12px; color: #666;'>Police Logo</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    # Divider with better styling
    st.markdown(
        "<hr style='height: 2px; background: linear-gradient(90deg, #1f77b4, #ff7f0e); border: none; margin: 20px 0;'>", 
        unsafe_allow_html=True
    )
    
    # Filters section
    return create_inline_filters(loaded_data)

def get_last_updated_date(loaded_data):
    """Extract and format the last updated date"""
    if 'crime_incidents' in loaded_data and not loaded_data['crime_incidents'].empty:
        latest_date = loaded_data['crime_incidents']['date_loaded'].max()
        if pd.notna(latest_date):
            # Handle different date formats
            if ' ' in str(latest_date):
                return latest_date.split()[0]
            else:
                return latest_date
    return "Loading..."

def get_total_records(loaded_data):
    """Get total number of crime incidents"""
    if 'crime_incidents' in loaded_data and not loaded_data['crime_incidents'].empty:
        return len(loaded_data['crime_incidents'])
    return 0

def create_inline_filters(loaded_data):
    """
    Create inline filter controls in main content area
    """
    st.markdown(
        """
        <div class="filter-section">
            <h3 style='margin-bottom: 20px; color: #1f77b4;'>🔍 Data Filters</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Create 4 columns for filters
    col1, col2, col3, col4 = st.columns(4)
    
    filters = {}
    
    with col1:
        st.markdown("**Police Force**")
        if 'police_forces' in loaded_data and not loaded_data['police_forces'].empty:
            force_options = ["All Forces"] + loaded_data['police_forces']['force_name'].tolist()
            selected_force = st.selectbox(
                "police_force_selector",
                options=force_options,
                index=0,
                help="Select specific police force or view all",
                label_visibility="collapsed"
            )
            filters['force'] = selected_force
        else:
            st.selectbox(
                "Police Force", 
                ["Loading data..."], 
                disabled=True,
                label_visibility="collapsed"
            )
            filters['force'] = "All Forces"
    
    with col2:
        st.markdown("**Time Period**")
        if 'crime_incidents' in loaded_data and not loaded_data['crime_incidents'].empty:
            date_options = ["All Months"] + sorted(loaded_data['crime_incidents']['month'].unique(), reverse=True)
            selected_dates = st.multiselect(
                "month_selector",
                options=date_options,
                default=["All Months"],
                help="Select specific months or view all data",
                label_visibility="collapsed"
            )
            # Convert "All Months" to actual dates
            if "All Months" in selected_dates or not selected_dates:
                filters['dates'] = date_options[1:]  # All actual dates
            else:
                filters['dates'] = selected_dates
        else:
            st.multiselect(
                "Months", 
                ["Loading data..."], 
                disabled=True,
                label_visibility="collapsed"
            )
            filters['dates'] = []
    
    with col3:
        st.markdown("**Crime Types**")
        if 'crime_categories' in loaded_data and not loaded_data['crime_categories'].empty:
            crime_options = ["All Crime Types"] + loaded_data['crime_categories']['category_name'].tolist()
            selected_crimes = st.multiselect(
                "crime_type_selector",
                options=crime_options,
                default=["All Crime Types"],
                help="Select specific crime types or view all",
                label_visibility="collapsed"
            )
            # Convert "All Crime Types" to actual crimes
            if "All Crime Types" in selected_crimes or not selected_crimes:
                filters['crimes'] = crime_options[1:]  # All actual crimes
            else:
                filters['crimes'] = selected_crimes
        else:
            st.multiselect(
                "Crime Types", 
                ["Loading data..."], 
                disabled=True,
                label_visibility="collapsed"
            )
            filters['crimes'] = []
    
    with col4:
        st.markdown("**Severity Level**")
        severity_options = ["All Levels", "Low (1-2)", "Medium (3)", "High (4-5)"]
        selected_severity = st.selectbox(
            "severity_selector",
            options=severity_options,
            index=0,
            help="Filter by crime severity level",
            label_visibility="collapsed"
        )
        filters['severity'] = selected_severity
    
    # Quick stats below filters
    if loaded_data.get('crime_incidents', pd.DataFrame()).empty == False:
        total_incidents = len(loaded_data['crime_incidents'])
        date_range = f"{loaded_data['crime_incidents']['month'].min()} to {loaded_data['crime_incidents']['month'].max()}"
        
        st.markdown(
            f"""
            <div style='background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); 
                        padding: 15px; border-radius: 10px; margin: 10px 0; 
                        border-left: 4px solid #1976d2;'>
                <div style='font-size: 14px; color: #1565c0;'>
                    📈 <strong>Dataset Summary:</strong> {total_incidents:,} incidents across {date_range}
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    # Add some spacing before next section
    st.markdown("<br>", unsafe_allow_html=True)
    
    return filters

    