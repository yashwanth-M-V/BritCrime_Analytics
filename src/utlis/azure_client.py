#!/usr/bin/env python3
"""
Azure Blob Storage Client - Store SQLite and CSV files for Streamlit
CORRECTED VERSION - Uses actual database schema
"""

import os
from azure.storage.blob import BlobServiceClient
import logging
from pathlib import Path
from datetime import datetime
import tempfile
import pandas as pd
from core.sqlite_manager import db_manager
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

class AzureBlobClient:
    def __init__(self):
        self.connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.container_name = "uk-crime-data"
        self.blob_service_client = None
        
        if self.connection_string:
            try:
                self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
                logger.info("Azure Blob Storage client initialized")
            except Exception as e:
                logger.warning(f"Azure Blob Storage connection failed: {e}")
        else:
            logger.warning("AZURE_STORAGE_CONNECTION_STRING not found - running in local mode only")
    
    def ensure_container_exists(self):
        """Create container if it doesn't exist"""
        if not self.blob_service_client:
            return False
            
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            if not container_client.exists():
                container_client.create_container()
                logger.info(f"Created Azure container: {self.container_name}")
            return True
        except Exception as e:
            logger.error(f"Container creation failed: {e}")
            return False
    
    def upload_sqlite_database(self):
        """Upload entire SQLite database to Azure Blob"""
        if not self.ensure_container_exists():
            return False
            
        try:
            db_path = Path("data/crime_data.db")
            if not db_path.exists():
                logger.error("SQLite database not found")
                return False
            
            # Upload SQLite file
            blob_name = "crime_database.db"
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, 
                blob=blob_name
            )
            
            with open(db_path, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)
            
            logger.info(f"SQLite database uploaded to Azure: {blob_name}")
            return True
            
        except Exception as e:
            logger.error(f"SQLite upload failed: {e}")
            return False
    
    def upload_streamlit_data(self):
        """Upload optimized data files for Streamlit app - USING CORRECT SCHEMA"""
        if not self.ensure_container_exists():
            return False
            
        try:
            conn = db_manager.connect()
            
            # CORRECTED QUERIES - Using actual column names from your database
            datasets = {
                "crime_incidents": """
                    SELECT 
                        id, crime_api_id, persistent_id, category, location_type,
                        location_subtype, context, latitude, longitude, street_id,
                        street_name, outcome_status_category, outcome_status_date,
                        month, date_loaded
                    FROM crime_incidents
                """,
                "crime_summary": """
                    SELECT * FROM crime_summary
                """,
                "crime_categories": """
                    SELECT * FROM crime_categories
                """,
                "police_forces": """
                    SELECT * FROM police_forces
                """,
                "crime_trends": """
                    SELECT 
                        month,
                        category,
                        COUNT(*) as incident_count
                    FROM crime_incidents 
                    GROUP BY month, category
                    ORDER BY month
                """,
                "crime_locations": """
                    SELECT 
                        crime_api_id, category, month, latitude, longitude, 
                        street_name
                    FROM crime_incidents 
                    WHERE latitude IS NOT NULL 
                    AND longitude IS NOT NULL
                """,
                "crime_severity": """
                    SELECT 
                        ci.category,
                        cc.severity_level,
                        COUNT(*) as incident_count
                    FROM crime_incidents ci
                    LEFT JOIN crime_categories cc ON ci.category = cc.category_id
                    GROUP BY ci.category, cc.severity_level
                    ORDER BY incident_count DESC
                """
            }
            
            for dataset_name, query in datasets.items():
                try:
                    df = pd.read_sql_query(query, conn)
                    
                    # Save to temporary CSV
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
                        csv_path = f.name
                        df.to_csv(csv_path, index=False)
                    
                    # Upload to Azure
                    blob_name = f"streamlit/{dataset_name}.csv"
                    blob_client = self.blob_service_client.get_blob_client(
                        container=self.container_name, 
                        blob=blob_name
                    )
                    
                    with open(csv_path, "rb") as data:
                        blob_client.upload_blob(data, overwrite=True)
                    
                    # Clean up temp file
                    Path(csv_path).unlink()
                    
                    logger.info(f"Uploaded {blob_name}: {len(df):,} records")
                    
                except Exception as e:
                    logger.error(f"Failed to process {dataset_name}: {e}")
                    continue
            
            conn.close()
            logger.info("All Streamlit datasets uploaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Streamlit data upload failed: {e}")
            return False
    
    def download_streamlit_data(self, dataset_name: str) -> pd.DataFrame:
        """Download dataset from Azure for Streamlit app"""
        if not self.blob_service_client:
            # Fallback to local database
            return self._get_data_from_local_db(dataset_name)
            
        try:
            blob_name = f"streamlit/{dataset_name}.csv"
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            # Check if blob exists
            if not blob_client.exists():
                logger.warning(f"Blob {blob_name} not found in Azure, falling back to local")
                return self._get_data_from_local_db(dataset_name)
            
            # Download to temporary file
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False) as f:
                download_path = f.name
                download_stream = blob_client.download_blob()
                download_stream.readinto(f)
            
            # Read into DataFrame
            df = pd.read_csv(download_path)
            
            # Clean up temp file
            Path(download_path).unlink()
            
            logger.info(f"Downloaded {dataset_name} from Azure: {len(df):,} records")
            return df
            
        except Exception as e:
            logger.warning(f"Azure download failed for {dataset_name}, falling back to local: {e}")
            return self._get_data_from_local_db(dataset_name)
    
    def _get_data_from_local_db(self, dataset_name: str) -> pd.DataFrame:
        """Fallback to local database if Azure fails"""
        try:
            conn = db_manager.connect()
            
            queries = {
                "crime_incidents": "SELECT * FROM crime_incidents",
                "crime_summary": "SELECT * FROM crime_summary",
                "crime_categories": "SELECT * FROM crime_categories",
                "police_forces": "SELECT * FROM police_forces",
                "crime_trends": """
                    SELECT 
                        month,
                        category,
                        COUNT(*) as incident_count
                    FROM crime_incidents 
                    GROUP BY month, category
                    ORDER BY month
                """,
                "crime_locations": """
                    SELECT 
                        crime_api_id, category, month, latitude, longitude, 
                        street_name
                    FROM crime_incidents 
                    WHERE latitude IS NOT NULL 
                    AND longitude IS NOT NULL
                """,
                "crime_severity": """
                    SELECT 
                        ci.category,
                        cc.severity_level,
                        COUNT(*) as incident_count
                    FROM crime_incidents ci
                    LEFT JOIN crime_categories cc ON ci.category = cc.category_id
                    GROUP BY ci.category, cc.severity_level
                    ORDER BY incident_count DESC
                """
            }
            
            if dataset_name in queries:
                df = pd.read_sql_query(queries[dataset_name], conn)
            else:
                df = pd.DataFrame()
            
            conn.close()
            
            if not df.empty:
                logger.info(f"Loaded {dataset_name} from local database: {len(df):,} records")
            else:
                logger.warning(f"No data found for {dataset_name} in local database")
            
            return df
            
        except Exception as e:
            logger.error(f"Local database fallback failed for {dataset_name}: {e}")
            return pd.DataFrame()
    
    def get_upload_status(self):
        """Check what files are available in Azure"""
        if not self.blob_service_client:
            return {"status": "not_configured"}
            
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            blobs = list(container_client.list_blobs())
            
            status = {
                "status": "connected",
                "container": self.container_name,
                "blobs": [blob.name for blob in blobs],
                "total_files": len(blobs)
            }
            return status
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def list_available_datasets(self):
        """List all datasets available for Streamlit"""
        status = self.get_upload_status()
        
        if status["status"] != "connected":
            return ["local_fallback"]
            
        streamlit_blobs = [blob for blob in status["blobs"] if blob.startswith("streamlit/")]
        datasets = [blob.replace("streamlit/", "").replace(".csv", "") for blob in streamlit_blobs]
        
        return datasets

# Singleton instance
azure_client = AzureBlobClient()