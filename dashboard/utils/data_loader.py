#!/usr/bin/env python3
"""
Data Loader - Connects to Azure Blob Storage and loads datasets
"""

import pandas as pd
import streamlit as st
from azure.storage.blob import BlobServiceClient
import os
import io

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data_from_azure():
    """
    Load all datasets from Azure Blob Storage
    Returns dictionary of DataFrames
    """
    try:
        # Get connection string from environment or Streamlit secrets
        connection_string = (
            os.getenv("AZURE_STORAGE_CONNECTION_STRING") or
            st.secrets.get("AZURE_STORAGE_CONNECTION_STRING", "")
        )
        
        if not connection_string:
            st.error("Azure Storage connection string not found")
            return {}
        
        # Initialize Blob Service Client
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_name = "uk-crime-data"
        
        # Datasets to load
        datasets = {
            "crime_incidents": "streamlit/crime_incidents.csv",
            "crime_summary": "streamlit/crime_summary.csv", 
            "crime_categories": "streamlit/crime_categories.csv",
            "crime_trends": "streamlit/crime_trends.csv",
            "crime_locations": "streamlit/crime_locations.csv",
            "crime_severity": "streamlit/crime_severity.csv",
            "police_forces": "streamlit/police_forces.csv"
        }
        
        loaded_data = {}
        
        for data_name, blob_path in datasets.items():
            try:
                # Get blob client
                blob_client = blob_service_client.get_blob_client(
                    container=container_name, 
                    blob=blob_path
                )
                
                # Download blob content
                download_stream = blob_client.download_blob()
                content = download_stream.readall()
                
                # Convert to DataFrame
                df = pd.read_csv(io.BytesIO(content))
                loaded_data[data_name] = df
                
                st.success(f"Loaded {data_name}: {len(df):,} records")
                
            except Exception as e:
                st.warning(f"Could not load {data_name}: {e}")
                # Create empty DataFrame as fallback
                loaded_data[data_name] = pd.DataFrame()
        
        return loaded_data
        
    except Exception as e:
        st.error(f"Failed to connect to Azure: {e}")
        return {}

def get_data_summary(loaded_data):
    """Get summary statistics of loaded data"""
    summary = {}
    for name, df in loaded_data.items():
        summary[name] = {
            'records': len(df),
            'columns': list(df.columns) if not df.empty else [],
            'date_range': df['month'].unique().tolist() if 'month' in df.columns and not df.empty else []
        }
    return summary