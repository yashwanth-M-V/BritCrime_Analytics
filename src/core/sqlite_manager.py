import sqlite3
import pandas as pd
import logging
from pathlib import Path
import numpy as np

logger = logging.getLogger(__name__)

class SQLiteManager:
    def __init__(self, db_path: str = "data/crime_data.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = None
        
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            logger.info(f"Connected to SQLite database: {self.db_path}")
            return self.connection
        except sqlite3.Error as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def initialize_database(self):
        """Create tables and initial setup based on ACTUAL API structure"""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            # Read and execute schema
            schema_file = Path("sql/sql_schema.sql")
            if schema_file.exists():
                with open(schema_file, 'r') as f:
                    schema_sql = f.read()
                cursor.executescript(schema_sql)
                logger.info("Database schema created successfully")
            else:
                logger.error("Schema file not found")
                
            # Insert initial reference data based on ACTUAL crime categories found
            self._insert_reference_data(conn)
            
            conn.commit()
            logger.info("Database initialization completed")
            
        except sqlite3.Error as e:
            logger.error(f"Database initialization failed: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def _insert_reference_data(self, conn):
        """Insert police forces and crime categories based on ACTUAL data"""
        cursor = conn.cursor()
        
        # Police forces we're tracking (from API explorer)
        police_forces = [
            ('metropolitan', 'Metropolitan Police'),
            ('west-midlands', 'West Midlands Police'), 
            ('greater-manchester', 'Greater Manchester Police')
        ]
        
        cursor.executemany(
            "INSERT OR IGNORE INTO police_forces (force_id, force_name) VALUES (?, ?)",
            police_forces
        )
        
        # Crime categories from ACTUAL API responses with realistic severity
        crime_categories = [
            ('anti-social-behaviour', 'Anti-social behaviour', 2),
            ('burglary', 'Burglary', 4),
            ('criminal-damage-arson', 'Criminal damage and arson', 3),
            ('drugs', 'Drugs', 3),
            ('possession-of-weapons', 'Possession of weapons', 5),
            ('public-order', 'Public order', 3),
            ('robbery', 'Robbery', 5),
            ('shoplifting', 'Shoplifting', 2),
            ('theft-from-the-person', 'Theft from the person', 4),
            ('vehicle-crime', 'Vehicle crime', 3),
            ('violent-crime', 'Violent crime', 5),
            ('other-crime', 'Other crime', 1),
            ('other-theft', 'Other theft', 2),
            ('bicycle-theft', 'Bicycle theft', 2)
        ]
        
        cursor.executemany(
            """INSERT OR IGNORE INTO crime_categories 
               (category_id, category_name, severity_level) VALUES (?, ?, ?)""",
            crime_categories
        )
        
        logger.info("Reference data inserted based on actual API structure")
    
    def prepare_crime_data(self, df: pd.DataFrame, force_id: str):
        """
        Transform raw API data to match our database schema
        Based on ACTUAL column structure we discovered
        """
        try:
            # Create a copy to avoid modifying original
            processed_df = df.copy()
            
            # Map API columns to our database schema
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
            
            # Rename columns to match our schema
            processed_df = processed_df.rename(columns=column_mapping)
            
            # Ensure we have all required columns (add missing ones as None)
            required_columns = list(column_mapping.values())
            for col in required_columns:
                if col not in processed_df.columns:
                    processed_df[col] = None
            
            # Select only the columns we need
            processed_df = processed_df[required_columns]
            
            # Convert data types based on ACTUAL API data
            processed_df['latitude'] = pd.to_numeric(processed_df['latitude'], errors='coerce')
            processed_df['longitude'] = pd.to_numeric(processed_df['longitude'], errors='coerce')
            processed_df['street_id'] = pd.to_numeric(processed_df['street_id'], errors='coerce').astype('Int64')
            processed_df['crime_api_id'] = pd.to_numeric(processed_df['crime_api_id'], errors='coerce').astype('Int64')
            
            # Handle missing values
            processed_df = processed_df.replace([np.nan], [None])
            
            logger.info(f"Prepared {len(processed_df)} records for database insertion")
            return processed_df
            
        except Exception as e:
            logger.error(f"Data preparation failed: {e}")
            raise
    
    def insert_crime_data(self, df: pd.DataFrame, force_id: str):
        """Insert prepared crime data into database"""
        try:
            conn = self.connect()
            
            # Prepare the data first
            processed_df = self.prepare_crime_data(df, force_id)
            
            # Insert data
            processed_df.to_sql('crime_incidents', conn, if_exists='append', index=False, 
                              method='multi', chunksize=1000)
            
            logger.info(f"Inserted {len(processed_df)} crime records for {force_id}")
            
            # Update street reference table
            self._update_street_reference(conn, processed_df)
            
            # Update summary statistics
            self._update_crime_summary(conn, force_id)
            
            conn.commit()
            
        except Exception as e:
            logger.error(f"Failed to insert crime data: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def _update_street_reference(self, conn, df: pd.DataFrame):
        """Update street reference table with new streets"""
        cursor = conn.cursor()
        
        # Get unique streets from the data
        streets = df[['street_id', 'street_name']].dropna().drop_duplicates()
        
        for _, street in streets.iterrows():
            cursor.execute("""
                INSERT OR REPLACE INTO street_reference 
                (street_id, street_name, last_seen) 
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (street['street_id'], street['street_name']))
    
    def _update_crime_summary(self, conn, force_id: str):
        """Update aggregated crime summary table"""
        cursor = conn.cursor()
        
        # Clear existing summary for this force
        cursor.execute("DELETE FROM crime_summary WHERE police_force = ?", (force_id,))
        
        # Insert new summary
        summary_query = """
        INSERT INTO crime_summary (month, police_force, crime_category, incident_count, high_severity_count)
        SELECT 
            month,
            ? as police_force,
            category as crime_category,
            COUNT(*) as incident_count,
            SUM(CASE WHEN cc.severity_level >= 4 THEN 1 ELSE 0 END) as high_severity_count
        FROM crime_incidents ci
        LEFT JOIN crime_categories cc ON ci.category = cc.category_id
        WHERE ci.month IS NOT NULL AND ci.category IS NOT NULL
        GROUP BY month, category
        """
        
        cursor.execute(summary_query, (force_id,))
        logger.info(f"Crime summary updated for {force_id}")

# Singleton instance
db_manager = SQLiteManager()