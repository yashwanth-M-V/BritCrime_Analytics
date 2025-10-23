# pages/1_overview.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

from utils.data_loader import load_data_from_azure
from utils.sidebar import create_sidebar

st.set_page_config(page_title="Overview - UK Crime Analytics", layout="wide")

# Get filters from sidebar first
filters = create_sidebar()

st.title("📊 Crime Overview Dashboard")

# Load data directly using cached function
with st.spinner("Loading crime data..."):
    data = load_data_from_azure(verbose=False)

# Check if data loaded successfully
if not data:
    st.error("❌ Failed to load data from Azure Storage")
    st.info("Please check your connection and try again")
    st.stop()

# Check if we have actual data
if all(df.empty for df in data.values()):
    st.warning("⚠️ Data loaded but all datasets are empty")
    st.stop()

# Get the dataframes
crime_incidents = data.get('crime_incidents', pd.DataFrame())
crime_summary = data.get('crime_summary', pd.DataFrame())

# Apply filters to the data
def apply_filters(df, filters):
    """Apply sidebar filters to dataframe"""
    filtered_df = df.copy()
    
    # Police Force filter
    if filters.get('police_force') and filters['police_force'] != "All Forces":
        if 'force_name' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['force_name'] == filters['police_force']]
    
    # Time Period filter
    if filters.get('time_period') and filters['time_period'] != "All Periods":
        if 'month' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['month'] == filters['time_period']]
    
    # Crime Types filter
    if filters.get('crime_types'):
        if 'crime_type' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['crime_type'].isin(filters['crime_types'])]
    
    # Severity Level filter
    if filters.get('severity_level'):
        if 'severity_level' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['severity_level'].isin(filters['severity_level'])]
    
    return filtered_df

# Apply filters to both datasets
filtered_incidents = apply_filters(crime_incidents, filters)
filtered_summary = apply_filters(crime_summary, filters)

# Show filter status and record count
st.write(f"**Active Filters:** {filters}")
st.success(f"✅ Showing {len(filtered_incidents):,} filtered crime incidents (from {len(crime_incidents):,} total)")

# Calculate KPIs using FILTERED data
def calculate_kpis(filtered_data):
    total_incidents = len(filtered_data)
    
    # High severity incidents
    high_severity = len(filtered_data[filtered_data['severity_level'] == 'High']) if 'severity_level' in filtered_data.columns else 0
    
    # Clearance rate
    if 'outcome' in filtered_data.columns:
        cleared = filtered_data[filtered_data['outcome'].str.contains('cleared|solved', case=False, na=False)]
        clearance_rate = (len(cleared) / total_incidents * 100) if total_incidents > 0 else 0
    else:
        clearance_rate = 0
    
    # Average time to outcome
    avg_time = 0
    if all(col in filtered_data.columns for col in ['reported_date', 'outcome_date']):
        filtered_data['reported_date'] = pd.to_datetime(filtered_data['reported_date'])
        filtered_data['outcome_date'] = pd.to_datetime(filtered_data['outcome_date'])
        time_diff = (filtered_data['outcome_date'] - filtered_data['reported_date']).dt.days
        avg_time = time_diff.mean() if not time_diff.empty else 0
    
    return total_incidents, high_severity, clearance_rate, avg_time

# Use FILTERED data for KPIs
total_incidents, high_severity, clearance_rate, avg_time = calculate_kpis(filtered_incidents)

# 1. KPI CARDS - Top Row
st.subheader("Key Performance Indicators")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Incidents", 
        value=f"{total_incidents:,}",
        delta="-2.1%"  # You can calculate this from previous period
    )

with col2:
    st.metric(
        label="High Severity Crimes", 
        value=f"{high_severity:,}",
        delta="+5.3%" if high_severity > 0 else "0%"
    )

with col3:
    st.metric(
        label="Clearance Rate", 
        value=f"{clearance_rate:.1f}%",
        delta="+1.2%"
    )

with col4:
    st.metric(
        label="Avg Time to Outcome", 
        value=f"{avg_time:.1f} days",
        delta="-0.5"
    )

st.markdown("---")

# 2. 7-DAY SPARKLINE (You'll need to implement this with actual date-based data)
st.subheader("7-Day Incident Trend")
st.info("📈 Trend chart will appear here when date-based data is available")

# 3. TWO-COLUMN LAYOUT FOR CATEGORIES AND STREETS
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Top 5 Crime Categories")
    
    # Use FILTERED data for categories
    if not filtered_incidents.empty and 'crime_type' in filtered_incidents.columns:
        top_categories = filtered_incidents['crime_type'].value_counts().head(5)
        
        if not top_categories.empty:
            fig_categories = px.bar(
                x=top_categories.values,
                y=top_categories.index,
                orientation='h',
                color=top_categories.values,
                color_continuous_scale='reds'
            )
            
            fig_categories.update_layout(
                height=300,
                xaxis_title="Number of Incidents",
                yaxis_title="",
                showlegend=False
            )
            
            st.plotly_chart(fig_categories, use_container_width=True)
        else:
            st.info("No data available for selected filters")
    else:
        st.info("Category data not available")

with col_right:
    st.subheader("Top 10 Streets by Incidents")
    
    # Use FILTERED data for streets
    if not filtered_summary.empty and 'street_name' in filtered_summary.columns:
        top_streets = filtered_summary.nlargest(10, 'incident_count')
        
        if not top_streets.empty:
            fig_streets = px.bar(
                x=top_streets['incident_count'],
                y=top_streets['street_name'],
                orientation='h',
                color=top_streets['incident_count'],
                color_continuous_scale='blues'
            )
            
            fig_streets.update_layout(
                height=300,
                xaxis_title="Number of Incidents",
                yaxis_title="",
                showlegend=False
            )
            
            st.plotly_chart(fig_streets, use_container_width=True)
        else:
            st.info("No data available for selected filters")
    else:
        st.info("Street data not available")

# 4. MAP PREVIEW
st.subheader("Crime Hotspots Map")

# Apply filters to locations data too
crime_locations = data.get('crime_locations', pd.DataFrame())
if not crime_locations.empty:
    filtered_locations = apply_filters(crime_locations, filters)
    
    if not filtered_locations.empty and all(col in filtered_locations.columns for col in ['latitude', 'longitude']):
        st.map(filtered_locations[['latitude', 'longitude']])
    else:
        st.info("Map coordinates not available for current filters")
else:
    st.info("Location data not available")

st.markdown("---")
st.caption("Last updated: 2025-10-20 | Data source: UK Police Data")