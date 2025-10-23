#!/usr/bin/env python3
"""
Data Processor - Handles data cleaning and transformation
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List
from core.config import config

logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self):
        self.required_columns = [
            'category', 'location_type', 'context', 'persistent_id', 'id',
            'location_subtype', 'month', 'location.latitude', 'location.street.id',
            'location.street.name', 'location.longitude', 'outcome_status.category',
            'outcome_status.date', 'force_id'
        ]
    
    def validate_data(self, df: pd.DataFrame, force_id: str) -> bool:
        """Validate that DataFrame has required structure"""
        if df.empty:
            logger.warning(f"Empty DataFrame for {force_id}")
            return False
        
        # Check for minimum required columns
        min_required = ['category', 'month', 'id', 'force_id']
        missing_columns = [col for col in min_required if col not in df.columns]
        
        if missing_columns:
            logger.error(f"Missing required columns for {force_id}: {missing_columns}")
            return False
        
        return True
    
    def clean_crime_data(self, df: pd.DataFrame, force_id: str) -> pd.DataFrame:
        """
        Clean and transform raw crime data
        Returns DataFrame ready for database insertion
        """
        try:
            if not self.validate_data(df, force_id):
                return pd.DataFrame()
            
            # Create a working copy
            processed_df = df.copy()
            
            # 1. Handle missing columns (different forces have different structures)
            for col in self.required_columns:
                if col not in processed_df.columns:
                    processed_df[col] = None
            
            # 2. Map columns to database schema
            column_mapping = {
                'id': 'crime_api_id',
                'persistent_id': 'persistent_id',
                'category': 'category',
                'location_type': 'location_type',
                'location_subtype': 'location_subtype',
                'context': 'context',
                'location.latitude': 'latitude',
                'location.longitude': 'longitude',
                'location.street.id': 'street_id',
                'location.street.name': 'street_name',
                'outcome_status.category': 'outcome_status_category',
                'outcome_status.date': 'outcome_status_date',
                'month': 'month'
            }
            
            processed_df = processed_df.rename(columns=column_mapping)
            
            # 3. Select only the columns we need for database
            final_columns = list(column_mapping.values())
            processed_df = processed_df[final_columns]
            
            # 4. Convert data types
            processed_df = self._convert_data_types(processed_df)
            
            # 5. Handle missing values
            processed_df = self._handle_missing_values(processed_df)
            
            # 6. Data quality checks
            processed_df = self._quality_checks(processed_df, force_id)
            
            logger.info(f"Cleaned {len(processed_df)} records for {force_id}")
            return processed_df
            
        except Exception as e:
            logger.error(f"Data cleaning failed for {force_id}: {e}")
            return pd.DataFrame()
    
    def _convert_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert columns to proper data types"""
        processed_df = df.copy()
        
        # Convert numeric fields
        numeric_columns = ['latitude', 'longitude', 'street_id', 'crime_api_id']
        for col in numeric_columns:
            if col in processed_df.columns:
                processed_df[col] = pd.to_numeric(processed_df[col], errors='coerce')
        
        # Convert street_id and crime_api_id to nullable integers
        if 'street_id' in processed_df.columns:
            processed_df['street_id'] = processed_df['street_id'].astype('Int64')
        if 'crime_api_id' in processed_df.columns:
            processed_df['crime_api_id'] = processed_df['crime_api_id'].astype('Int64')
        
        return processed_df
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing and null values"""
        processed_df = df.copy()
        
        # Replace pandas NA with None for database compatibility
        processed_df = processed_df.replace({pd.NA: None, np.nan: None})
        
        # Empty strings to None
        string_columns = processed_df.select_dtypes(include=['object']).columns
        for col in string_columns:
            processed_df[col] = processed_df[col].replace('', None)
        
        return processed_df
    
    def _quality_checks(self, df: pd.DataFrame, force_id: str) -> pd.DataFrame:
        """Perform data quality checks"""
        processed_df = df.copy()
        
        # Remove records missing critical data
        initial_count = len(processed_df)
        
        # Must have crime category and month
        processed_df = processed_df.dropna(subset=['category', 'month'])
        
        # Must have valid crime_api_id
        processed_df = processed_df[processed_df['crime_api_id'].notna()]
        
        removed_count = initial_count - len(processed_df)
        if removed_count > 0:
            logger.warning(f"Removed {removed_count} invalid records for {force_id}")
        
        # Check for duplicate crime IDs
        duplicates = processed_df.duplicated(subset=['crime_api_id'], keep=False)
        if duplicates.any():
            duplicate_count = duplicates.sum()
            logger.warning(f"Found {duplicate_count} duplicate crime IDs for {force_id}")
            processed_df = processed_df.drop_duplicates(subset=['crime_api_id'], keep='first')
        
        return processed_df
    
    def process_multiple_forces(self, data_dict: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Process data for multiple forces"""
        processed_data = {}
        
        for force_id, raw_df in data_dict.items():
            if not raw_df.empty:
                cleaned_df = self.clean_crime_data(raw_df, force_id)
                if not cleaned_df.empty:
                    processed_data[force_id] = cleaned_df
                    logger.info(f"Processed {len(cleaned_df)} records for {force_id}")
                else:
                    logger.warning(f"No valid data after processing for {force_id}")
            else:
                logger.warning(f"No raw data to process for {force_id}")
        
        return processed_data

# Singleton instance
data_processor = DataProcessor()