#!/usr/bin/env python3
"""
KPI Cards Component - Metric cards with trends
"""

import streamlit as st
import numpy as np
import pandas as pd

def create_kpi_cards(loaded_data, filters):
    """
    Create KPI cards row with metrics and deltas
    """
    st.header("📊 Executive Overview")
    
    # Calculate metrics
    metrics = calculate_metrics(loaded_data, filters)
    
    # Create 4 columns for KPI cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Incidents",
            value=f"{metrics['total_incidents']:,}",
            delta=f"{metrics['incidents_delta']}%"
        )
    
    with col2:
        st.metric(
            label="High Severity Crimes",
            value=f"{metrics['high_severity']:,}",
            delta=f"{metrics['severity_delta']}%"
        )
    
    with col3:
        st.metric(
            label="Clearance Rate",
            value=f"{metrics['clearance_rate']}%",
            delta=f"{metrics['clearance_delta']}%"
        )
    
    with col4:
        st.metric(
            label="Avg Severity Score",
            value=f"{metrics['avg_severity']:.1f}",
            delta=f"{metrics['severity_score_delta']:.1f}"
        )
    
    st.markdown("---")

def calculate_metrics(loaded_data, filters):
    """
    Calculate all KPI metrics
    """
    incidents_df = loaded_data.get('crime_incidents', pd.DataFrame())
    categories_df = loaded_data.get('crime_categories', pd.DataFrame())
    
    if incidents_df.empty:
        return {
            'total_incidents': 0,
            'high_severity': 0,
            'clearance_rate': 0,
            'avg_severity': 0,
            'incidents_delta': 0,
            'severity_delta': 0,
            'clearance_delta': 0,
            'severity_score_delta': 0
        }
    
    # Apply filters
    filtered_df = apply_filters(incidents_df, categories_df, filters)
    
    # Calculate metrics
    total_incidents = len(filtered_df)
    
    # High severity crimes (level 4-5)
    high_severity = len(filtered_df[filtered_df['severity_level'] >= 4]) if 'severity_level' in filtered_df.columns else 0
    
    # Clearance rate (non-null outcomes)
    clearance_rate = (filtered_df['outcome_status_category'].notna().sum() / total_incidents * 100) if 'outcome_status_category' in filtered_df.columns else 0
    
    # Average severity
    avg_severity = filtered_df['severity_level'].mean() if 'severity_level' in filtered_df.columns else 0
    
    # Dummy deltas (in real app, compare with previous period)
    incidents_delta = 5.2
    severity_delta = 12.1
    clearance_delta = -2.3
    severity_score_delta = 0.3
    
    return {
        'total_incidents': total_incidents,
        'high_severity': high_severity,
        'clearance_rate': round(clearance_rate, 1),
        'avg_severity': round(avg_severity, 1),
        'incidents_delta': incidents_delta,
        'severity_delta': severity_delta,
        'clearance_delta': clearance_delta,
        'severity_score_delta': severity_score_delta
    }

def apply_filters(incidents_df, categories_df, filters):
    """
    Apply filters to the data
    """
    filtered_df = incidents_df.copy()
    
    # Apply date filter
    if filters.get('dates'):
        filtered_df = filtered_df[filtered_df['month'].isin(filters['dates'])]
    
    # Apply crime type filter
    if filters.get('crimes') and 'category_name' in categories_df.columns:
        crime_codes = categories_df[categories_df['category_name'].isin(filters['crimes'])]['category_id'].tolist()
        filtered_df = filtered_df[filtered_df['category'].isin(crime_codes)]
    
    # Apply severity filter
    severity_filter = filters.get('severity', 'All')
    if severity_filter != "All":
        if severity_filter == "Low (1-2)":
            filtered_df = filtered_df[filtered_df['severity_level'] <= 2]
        elif severity_filter == "Medium (3)":
            filtered_df = filtered_df[filtered_df['severity_level'] == 3]
        elif severity_filter == "High (4-5)":
            filtered_df = filtered_df[filtered_df['severity_level'] >= 4]
    
    return filtered_df