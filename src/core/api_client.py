#!/usr/bin/env python3
"""
Police UK API Client - Handles data extraction from data.police.uk
"""

import requests
import pandas as pd
import logging
from typing import List, Dict, Tuple
import time
from core.config import config

logger = logging.getLogger(__name__)

class PoliceAPIClient:
    # Fixed central coordinates for key forces (Option 1)
    FORCE_COORDINATES: Dict[str, Tuple[float, float]] = {
        "metropolitan": (51.5074, -0.1278),         # London
        "west-midlands": (52.4895, -1.8980),       # Birmingham
        "greater-manchester": (53.4808, -2.2426),  # Manchester
    }

    def __init__(self):
        self.base_url = config.api.base_url
        self.timeout = config.api.timeout
        self.max_retries = config.api.max_retries

    def get_available_months(self) -> List[str]:
        """Get list of available months for data download"""
        try:
            url = f"{self.base_url}crimes-street-dates"
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()

            dates_data = response.json()
            available_months = [item['date'] for item in dates_data]

            logger.info(f"Found {len(available_months)} available months")
            return available_months

        except Exception as e:
            logger.error(f"Failed to fetch available months: {e}")
            return []

    def fetch_crime_data(self, force_id: str, month: str) -> pd.DataFrame:
        """
        Fetch crime data using fixed coordinates per force (Option 1).
        Returns DataFrame with raw API data.
        """
        if force_id not in self.FORCE_COORDINATES:
            logger.warning(f"No coordinates defined for {force_id}. Skipping...")
            return pd.DataFrame()

        lat, lng = self.FORCE_COORDINATES[force_id]
        url = f"{self.base_url}crimes-street/all-crime"
        params = {"lat": lat, "lng": lng, "date": month}

        logger.info(f"Fetching data for {force_id} - {month} (lat={lat}, lng={lng})")

        for attempt in range(self.max_retries):
            try:
                response = requests.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()

                crimes_data = response.json()
                if not crimes_data:
                    logger.warning(f"No data returned for {force_id} - {month}")
                    return pd.DataFrame()

                df = pd.json_normalize(crimes_data)
                df['force_id'] = force_id
                df['month'] = month

                logger.info(f"Retrieved {len(df)} records for {force_id} - {month}")
                return df

            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"Failed after {self.max_retries} attempts for {force_id} - {month}: {e}")
                    return pd.DataFrame()

                logger.warning(f"Attempt {attempt + 1} failed for {force_id} - {month}, retrying...")
                time.sleep(2)

        return pd.DataFrame()

    def fetch_multiple_forces(self, force_ids: List[str], months: List[str]) -> Dict[str, pd.DataFrame]:
        """
        Fetch data for multiple forces and months
        Returns dictionary with DataFrames for each force
        """
        all_data = {}

        for force_id in force_ids:
            force_data = []

            for month in months:
                df = self.fetch_crime_data(force_id, month)
                if not df.empty:
                    force_data.append(df)

                # Rate limiting
                time.sleep(0.5)

            if force_data:
                all_data[force_id] = pd.concat(force_data, ignore_index=True)
                logger.info(f"SUCESS: Combined {len(force_data)} months for {force_id}, total records: {len(all_data[force_id])}")
            else:
                logger.warning(f"No data retrieved for {force_id}")
                all_data[force_id] = pd.DataFrame()

        return all_data

    def get_recent_months(self, months_count: int = 12) -> List[str]:
        """Get list of recent months (default: last 12 months)"""
        available_months = self.get_available_months()
        if not available_months:
            return []

        available_months.sort(reverse=True)
        recent_months = available_months[:months_count]

        logger.info(f"Selected {len(recent_months)} recent months: {recent_months}")
        return recent_months


# Singleton instance
api_client = PoliceAPIClient()
