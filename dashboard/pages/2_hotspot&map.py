import streamlit as st
from components.header import create_header

st.title("🔥 Hotspots & Map Page")

loaded_data = st.session_state.get("loaded_data")
if not loaded_data:
    st.error("❌ Data not loaded. Please return to the main page.")
else:
    filters = create_header(loaded_data)
    st.write("🗺️ Placeholder: Heatmap & cluster visualization will appear here.")
