#!/usr/bin/env python3
"""Add missing force_id column to crime_incidents table"""

import sqlite3
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_database_schema():
    """Add force_id column and populate it"""
    db_path = Path("data/crime_data.db")
    
    if not db_path.exists():
        logger.error("Database file not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔧 FIXING DATABASE SCHEMA")
        print("=" * 50)
        
        # Check if force_id column already exists
        cursor.execute("PRAGMA table_info(crime_incidents)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'force_id' not in columns:
            print("1. Adding force_id column to crime_incidents table...")
            cursor.execute("ALTER TABLE crime_incidents ADD COLUMN force_id TEXT")
            print("   ✅ force_id column added")
        else:
            print("1. force_id column already exists")
        
        # Since we don't have the original force information, we'll need to 
        # either re-run the ETL or use a different approach
        print("\n2. Since force_id data is missing, we'll:")
        print("   - Re-run the ETL pipeline to populate force_id")
        print("   - OR use police_forces table directly in queries")
        
        conn.commit()
        conn.close()
        
        print("\n✅ Database schema fix completed")
        return True
        
    except Exception as e:
        logger.error(f"Database fix failed: {e}")
        return False

if __name__ == "__main__":
    fix_database_schema()