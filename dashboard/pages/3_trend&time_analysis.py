import streamlit as st
import pandas as pd
from components.header import create_header

st.title("📅 Trends & Time Analysis Page")

loaded_data = st.session_state.get("loaded_data")
if not loaded_data:
    st.error("❌ Data not loaded. Please return to the main page.")
else:
    filters = create_header(loaded_data)
    st.write("📊 Placeholder: Time series charts and heat tables will appear here.")
