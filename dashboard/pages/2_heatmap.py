import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
from datetime import datetime, timedelta
from utils.data_loader import load_data_from_azure
from utils.sidebar import create_sidebar

st.set_page_config(page_title="Heatmap & Hotspots - UK Crime Analytics", layout="wide")

# Get filters from sidebar
filters = create_sidebar()

st.title("🗺️ Crime Heatmap & Hotspots")

# Load data
with st.spinner("Loading crime data for mapping..."):
    data = load_data_from_azure(verbose=False)

if not data or all(df.empty for df in data.values()):
    st.error("Failed to load data")
    st.stop()

# Apply filters function (same as overview)
def apply_filters(df, filters):
    filtered_df = df.copy()
    
    if filters.get('police_force') and filters['police_force'] != "All Forces":
        if 'force_name' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['force_name'] == filters['police_force']]
    
    if filters.get('time_period') and filters['time_period'] != "All Periods":
        if 'month' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['month'] == filters['time_period']]
    
    if filters.get('crime_types'):
        if 'crime_type' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['crime_type'].isin(filters['crime_types'])]
    
    if filters.get('severity_level'):
        if 'severity_level' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['severity_level'].isin(filters['severity_level'])]
    
    return filtered_df

# Get and filter location data
crime_locations = data.get('crime_locations', pd.DataFrame())
crime_incidents = data.get('crime_incidents', pd.DataFrame())

if crime_locations.empty:
    st.warning("No location data available for mapping")
    st.stop()

# Apply filters
filtered_locations = apply_filters(crime_locations, filters)
filtered_incidents = apply_filters(crime_incidents, filters)

st.success(f"📍 Showing {len(filtered_locations):,} crime locations on map")

# Additional time-based filters for heatmap page
st.sidebar.markdown("---")
st.sidebar.subheader("🗓️ Timeframe Filter")
timeframe = st.sidebar.selectbox(
    "Select Timeframe",
    ["Last 7 days", "Last 30 days", "Last 90 days", "All available data"],
    index=3
)

# Prepare data for mapping
def prepare_map_data(locations_df, incidents_df):
    """Prepare data for pydeck layers"""
    
    # Ensure we have required columns
    if not all(col in locations_df.columns for col in ['latitude', 'longitude']):
        st.error("Latitude and longitude columns are required for mapping")
        return pd.DataFrame()
    
    # Merge with incident data for additional details
    merge_columns = []
    if 'incident_id' in locations_df.columns and 'incident_id' in incidents_df.columns:
        merge_columns = ['crime_type', 'month', 'outcome_status_category', 'street_name', 'severity_level']
        available_columns = [col for col in merge_columns if col in incidents_df.columns]
        
        if available_columns:
            map_data = locations_df.merge(
                incidents_df[['incident_id'] + available_columns], 
                on='incident_id', 
                how='left'
            )
        else:
            map_data = locations_df.copy()
    else:
        map_data = locations_df.copy()
    
    # Add weight for heatmap (based on severity if available)
    if 'severity_level' in map_data.columns:
        severity_weights = {'High': 3, 'Medium': 2, 'Low': 1}
        map_data['weight'] = map_data['severity_level'].map(severity_weights).fillna(1)
    else:
        map_data['weight'] = 1
    
    # Ensure numeric coordinates
    map_data['latitude'] = pd.to_numeric(map_data['latitude'], errors='coerce')
    map_data['longitude'] = pd.to_numeric(map_data['longitude'], errors='coerce')
    map_data = map_data.dropna(subset=['latitude', 'longitude'])
    
    return map_data

map_data = prepare_map_data(filtered_locations, filtered_incidents)

if map_data.empty:
    st.error("No valid location data available after filtering")
    st.stop()

# Calculate initial view state
def get_initial_view(data):
    """Calculate initial map view based on data bounds"""
    if data.empty:
        return {"latitude": 51.5074, "longitude": -0.1278, "zoom": 10, "pitch": 0, "bearing": 0}
    
    avg_lat = data['latitude'].mean()
    avg_lon = data['longitude'].mean()
    
    # Simple bounds calculation
    lat_range = data['latitude'].max() - data['latitude'].min()
    lon_range = data['longitude'].max() - data['longitude'].min()
    
    # Adjust zoom based on data spread
    zoom = 10 - max(lat_range, lon_range) * 50
    
    return {
        "latitude": avg_lat,
        "longitude": avg_lon,
        "zoom": max(8, min(12, zoom)),
        "pitch": 0,
        "bearing": 0
    }

initial_view = get_initial_view(map_data)

# Create pydeck layers
def create_map_layers(data):
    """Create multiple layers for the map"""
    layers = []
    
    # Layer 1: Heatmap
    heatmap_layer = pdk.Layer(
        "HeatmapLayer",
        data=data,
        get_position=["longitude", "latitude"],
        get_weight="weight",
        aggregation="MEAN",
        radius_pixels=50,
        intensity=1,
        threshold=0.5,
        color_range=[
            [0, 0, 0, 0],      # Transparent
            [255, 255, 178, 100],  # Light yellow
            [254, 204, 92, 150],   # Yellow
            [253, 141, 60, 200],   # Orange
            [240, 59, 32, 255],    # Red
            [189, 0, 38, 255]      # Dark red
        ]
    )
    layers.append(heatmap_layer)
    
    # Layer 2: Cluster Layer for high density areas
    cluster_layer = pdk.Layer(
        "HexagonLayer",
        data=data,
        get_position=["longitude", "latitude"],
        radius=100,
        elevation_scale=4,
        elevation_range=[0, 1000],
        extruded=True,
        coverage=1,
        auto_highlight=True
    )
    layers.append(cluster_layer)
    
    # Layer 3: Individual incident pins (only show when zoomed in)
    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        data=data,
        get_position=["longitude", "latitude"],
        get_fill_color=[255, 0, 0, 180],
        get_radius=50,
        radius_min_pixels=3,
        radius_max_pixels=10,
        pickable=True,
        auto_highlight=True
    )
    layers.append(scatter_layer)
    
    return layers

# Create the map
layers = create_map_layers(map_data)

# Tooltip for incident pins
tooltip = {
    "html": """
        <b>Category:</b> {crime_type} <br/>
        <b>Month:</b> {month} <br/>
        <b>Outcome:</b> {outcome_status_category} <br/>
        <b>Street:</b> {street_name} <br/>
        <b>Severity:</b> {severity_level}
    """,
    "style": {
        "backgroundColor": "steelblue",
        "color": "white"
    }
}

# Create the deck gl map
st.pydeck_chart(
    pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v10",
        initial_view_state=initial_view,
        layers=layers,
        tooltip=tooltip
    )
)

# Map controls and information
col1, col2, col3 = st.columns(3)

with col1:
    st.info("**Map Controls**")
    st.write("- **Zoom**: Scroll to zoom in/out")
    st.write("- **Click**: Select incidents")
    st.write("- **Drag**: Pan around the map")

with col2:
    st.info("**Layers Legend**")
    st.write("🔴 **Red Areas**: High crime density")
    st.write("🟡 **Yellow Areas**: Medium crime density")
    st.write("🔵 **Blue Areas**: Low crime density")
    st.write("⭕ **Circles**: Individual incidents")

with col3:
    st.info("**Data Summary**")
    st.write(f"**Total Points**: {len(map_data):,}")
    st.write(f"**Data Range**: {map_data['month'].min() if 'month' in map_data.columns else 'N/A'} to {map_data['month'].max() if 'month' in map_data.columns else 'N/A'}")
    
    if 'severity_level' in map_data.columns:
        severity_counts = map_data['severity_level'].value_counts()
        for level, count in severity_counts.items():
            st.write(f"**{level}**: {count:,}")

# Additional analytics below map
st.markdown("---")
st.subheader("📊 Hotspot Analysis")

col_analytics1, col_analytics2 = st.columns(2)

with col_analytics1:
    # Top hotspots by density
    st.write("**Top Crime Hotspots**")
    if 'street_name' in map_data.columns:
        hotspot_streets = map_data['street_name'].value_counts().head(10)
        for street, count in hotspot_streets.items():
            st.write(f"• {street}: {count:,} incidents")

with col_analytics2:
    # Time-based analysis
    st.write("**Temporal Patterns**")
    if 'month' in map_data.columns:
        monthly_trend = map_data['month'].value_counts().sort_index()
        st.line_chart(monthly_trend)

# Export and actions
st.markdown("---")
col_export1, col_export2 = st.columns(2)

with col_export1:
    if st.button("📥 Export Hotspot Data"):
        csv = map_data.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="crime_hotspots.csv",
            mime="text/csv"
        )

with col_export2:
    if st.button("🔄 Reset Map View"):
        st.rerun()

st.caption("💡 **Tip**: Zoom in to see individual incidents. Click on clusters to explore detailed information.")
