#!/usr/bin/env python3
"""
Main ETL Pipeline - Orchestrates the complete data flow
"""

import logging
import pandas as pd
from datetime import datetime
from core.api_client import api_client
from core.data_processor import data_processor
from core.sqlite_manager import db_manager
from core.config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/etl_pipeline.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class ETLPipeline:
    def __init__(self):
        self.police_forces = config.etl.police_forces
        self.months_to_fetch = config.etl.months_to_fetch
        
    def run(self):
        """Execute complete ETL pipeline"""
        logger.info("Starting ETL Pipeline")
        start_time = datetime.now()
        
        try:
            # EXTRACT PHASE
            logger.info("Starting EXTRACT phase")
            raw_data = self.extract_phase()
            
            if not raw_data:
                logger.error("EXTRACT phase failed - no data retrieved")
                return False
            
            # TRANSFORM PHASE  
            logger.info("Starting TRANSFORM phase")
            processed_data = self.transform_phase(raw_data)
            
            if not processed_data:
                logger.error("TRANSFORM phase failed - no processed data")
                return False
            
            # LOAD PHASE
            logger.info("Starting LOAD phase")
            load_success = self.load_phase(processed_data)
            
            if load_success:
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds() / 60
                logger.info(f"ETL Pipeline completed successfully in {duration:.2f} minutes")
                return True
            else:
                logger.error("LOAD phase failed")
                return False
                
        except Exception as e:
            logger.error(f"ETL Pipeline failed: {e}")
            return False
    
    def extract_phase(self) -> dict:
        """Extract data from police API"""
        try:
            # Get recent months
            recent_months = api_client.get_recent_months(self.months_to_fetch)
            if not recent_months:
                logger.error("No recent months available")
                return {}
            
            logger.info(f"Fetching data for {len(self.police_forces)} forces and {len(recent_months)} months")
            
            # Fetch data for all forces and months
            raw_data = api_client.fetch_multiple_forces(self.police_forces, recent_months)
            
            # Check if we got any data
            total_records = sum(len(df) for df in raw_data.values() if not df.empty)
            logger.info(f"EXTRACT phase completed: {total_records} total records retrieved")
            
            return raw_data
            
        except Exception as e:
            logger.error(f"EXTRACT phase failed: {e}")
            return {}
    
    def transform_phase(self, raw_data: dict) -> dict:
        """Transform and clean the extracted data"""
        try:
            processed_data = data_processor.process_multiple_forces(raw_data)
            
            total_processed = sum(len(df) for df in processed_data.values() if not df.empty)
            logger.info(f"TRANSFORM phase completed: {total_processed} records processed")
            
            return processed_data
            
        except Exception as e:
            logger.error(f"TRANSFORM phase failed: {e}")
            return {}
    
    def load_phase(self, processed_data: dict) -> bool:
        """Load processed data into database"""
        try:
            total_loaded = 0
            
            for force_id, df in processed_data.items():
                if not df.empty:
                    logger.info(f"Loading {len(df)} records for {force_id} into database")
                    db_manager.insert_crime_data(df, force_id)
                    total_loaded += len(df)
            
            logger.info(f"LOAD phase completed: {total_loaded} records loaded into database")
            return total_loaded > 0
            
        except Exception as e:
            logger.error(f"LOAD phase failed: {e}")
            return False
    def cloud_sync_phase(self) -> bool:
        """Sync data to Azure Blob Storage for Streamlit"""
        try:
            from utlis.azure_client import azure_client

            logger.info("Starting CLOUD SYNC phase")

            # Upload SQLite database
            db_uploaded = azure_client.upload_sqlite_database()

            # Upload Streamlit-optimized data
            data_uploaded = azure_client.upload_streamlit_data()

            # Get upload status
            status = azure_client.get_upload_status()

            if db_uploaded or data_uploaded:
                logger.info("CLOUD SYNC completed successfully")

                # Print status for verification
                print("\n" + "=" * 50)
                print("AZURE BLOB STORAGE STATUS:")
                print(f"Status: {status.get('status', 'unknown')}")
                print(f"Container: {status.get('container', 'N/A')}")
                print(f"Total files: {status.get('total_files', 0)}")
                if 'blobs' in status:
                    print("Files uploaded:")
                    for blob in status['blobs']:
                        print(f"  - {blob}")
                print("=" * 50)

                return True
            else:
                logger.warning("Cloud sync completed but no files were uploaded")
                return False

        except Exception as e:
            logger.error(f"Cloud sync phase failed: {e}")
            return False

def main():
    """Main function to run ETL pipeline"""
    pipeline = ETLPipeline()
    success = pipeline.run()
    
    if success:
        print("ETL Pipeline completed successfully!")
        print("Database is now ready for Power BI visualization")
    else:
        print("ETL Pipeline failed. Check logs for details.")
    
    return success

if __name__ == "__main__":
    main()