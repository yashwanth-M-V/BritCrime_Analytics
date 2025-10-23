#!/usr/bin/env python3
"""
API Explorer - First understand the data structure before designing database
"""

import requests
import json
import pandas as pd
import logging
from core.config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PoliceAPIExplorer:
    def __init__(self):
        self.base_url = config.api.base_url
        
    def get_available_forces(self):
        """Get list of available police forces"""
        try:
            response = requests.get(f"{self.base_url}forces")
            response.raise_for_status()
            forces = response.json()
            logger.info(f"Found {len(forces)} police forces")
            
            with open(config.DATA_DIR / "available_forces.json", 'w') as f:
                json.dump(forces, f, indent=2)
            return forces
        except Exception as e:
            logger.error(f"Failed to fetch forces: {e}")
            return []
    
    def get_force_coordinates(self, force_id: str):
        """Get a representative lat/lng for the force (from first neighbourhood)"""
        try:
            n_url = f"{self.base_url}{force_id}/neighbourhoods"
            n_resp = requests.get(n_url)
            n_resp.raise_for_status()
            neighbourhoods = n_resp.json()
            if not neighbourhoods:
                logger.warning(f"No neighbourhoods found for {force_id}")
                return None, None

            first_id = neighbourhoods[0]["id"]
            d_url = f"{self.base_url}{force_id}/{first_id}"
            d_resp = requests.get(d_url)
            d_resp.raise_for_status()
            details = d_resp.json()

            lat = details["centre"]["latitude"]
            lng = details["centre"]["longitude"]
            return lat, lng
        except Exception as e:
            logger.error(f"Failed to get coordinates for {force_id}: {e}")
            return None, None

    def explore_force_data(self, force_id: str, sample_month: str = "2024-01"):
        """Get sample crime data for a specific force and month"""
        try:
            # ✅ Get lat/lng for the force
            lat, lng = self.get_force_coordinates(force_id)
            if not lat or not lng:
                logger.warning(f"Skipping {force_id}: no coordinates found")
                return pd.DataFrame()
            
            url = f"{self.base_url}crimes-street/all-crime"
            params = {
                'lat': lat,
                'lng': lng,
                'date': sample_month
            }
            
            logger.info(f"Fetching sample data for {force_id} - {sample_month}")
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            crimes = response.json()
            logger.info(f"Retrieved {len(crimes)} sample crime records for {force_id}")
            
            if crimes:
                sample_file = config.DATA_DIR / "raw" / f"sample_{force_id}_{sample_month}.json"
                sample_file.parent.mkdir(parents=True, exist_ok=True)
                with open(sample_file, 'w') as f:
                    json.dump(crimes, f, indent=2)
                
                df = pd.json_normalize(crimes)
                self.analyze_data_structure(df, force_id)
                return df
            else:
                logger.warning(f"No data returned for {force_id} - {sample_month}")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Failed to explore force data for {force_id}: {e}")
            return pd.DataFrame()
    
    def analyze_data_structure(self, df: pd.DataFrame, force_id: str):
        """Analyze the structure of the returned data"""
        logger.info(f"\n=== DATA STRUCTURE ANALYSIS for {force_id} ===")
        logger.info(f"Shape: {df.shape}")
        logger.info(f"Columns: {list(df.columns)}")
        logger.info(f"Data types:\n{df.dtypes}")
        
        for col in df.columns:
            sample_value = df[col].iloc[0] if len(df) > 0 else None
            logger.info(f"Column '{col}': Sample = {sample_value} (Type: {type(sample_value)})")
        
        analysis = {
            'force_id': force_id,
            'total_columns': len(df.columns),
            'columns': list(df.columns),
            'data_types': {col: str(df[col].dtype) for col in df.columns},
            'sample_records': len(df)
        }
        
        analysis_file = config.DATA_DIR / f"column_analysis_{force_id}.json"
        with open(analysis_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        if len(df) > 0:
            csv_file = config.DATA_DIR / "raw" / f"sample_data_{force_id}.csv"
            df.to_csv(csv_file, index=False)
            logger.info(f"Sample data saved to: {csv_file}")

def main():
    explorer = PoliceAPIExplorer()
    forces = explorer.get_available_forces()
    
    target_forces = ['metropolitan', 'west-midlands', 'greater-manchester']
    all_samples = []
    for force in target_forces:
        sample_df = explorer.explore_force_data(force)
        if not sample_df.empty:
            all_samples.append(sample_df)
    
    if all_samples:
        comparison = {}
        for i, df in enumerate(all_samples):
            force = target_forces[i]
            comparison[force] = {
                'columns': list(df.columns),
                'shape': df.shape
            }
        
        comparison_file = config.DATA_DIR / "force_comparison.json"
        with open(comparison_file, 'w') as f:
            json.dump(comparison, f, indent=2)
        
        logger.info("✅ Data exploration completed. Check the generated files in data/ directory")

if __name__ == "__main__":
    main()
