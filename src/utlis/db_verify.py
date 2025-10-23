#!/usr/bin/env python3
"""
Database Verification Script
Check if data was loaded correctly into SQLite
"""

import sqlite3
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_database():
    """Verify database content and structure"""
    db_path = Path("data/crime_data.db")
    
    if not db_path.exists():
        logger.error("Database file not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 DATABASE VERIFICATION REPORT")
        print("=" * 50)
        
        # 1. Check table existence
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """)
        tables = cursor.fetchall()
        print(f"📊 Tables in database: {[table[0] for table in tables]}")
        print()
        
        # 2. Check record counts
        tables_to_check = ['crime_incidents', 'crime_summary', 'police_forces', 'crime_categories']
        
        for table in tables_to_check:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"📈 {table}: {count} records")
        
        print()
        
        # 3. Check crime incidents details
        cursor.execute("""
            SELECT 
                COUNT(*) as total_incidents,
                COUNT(DISTINCT crime_api_id) as unique_ids,
                MIN(month) as earliest_month,
                MAX(month) as latest_month,
                COUNT(DISTINCT category) as crime_types
            FROM crime_incidents
        """)
        stats = cursor.fetchone()
        print("📋 CRIME INCIDENTS SUMMARY:")
        print(f"   • Total incidents: {stats[0]}")
        print(f"   • Unique crime IDs: {stats[1]}")
        print(f"   • Date range: {stats[2]} to {stats[3]}")
        print(f"   • Crime types: {stats[4]}")
        print()
        
        # 4. Check crime categories distribution
        cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM crime_incidents 
            GROUP BY category 
            ORDER BY count DESC
            LIMIT 10
        """)
        print("🔎 TOP 10 CRIME CATEGORIES:")
        for category, count in cursor.fetchall():
            print(f"   • {category}: {count} incidents")
        
        print()
        
        # 5. Check police forces data
        cursor.execute("""
            SELECT reported_by, COUNT(*) as count
            FROM crime_incidents 
            GROUP BY reported_by
            ORDER BY count DESC
        """)
        print("👮 POLICE FORCES DATA:")
        for force, count in cursor.fetchall():
            print(f"   • {force}: {count} incidents")
        
        print()
        
        # 6. Check data quality
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN latitude IS NULL OR longitude IS NULL THEN 1 ELSE 0 END) as missing_coords,
                SUM(CASE WHEN outcome_status_category IS NULL THEN 1 ELSE 0 END) as missing_outcomes
            FROM crime_incidents
        """)
        quality = cursor.fetchone()
        print("✅ DATA QUALITY CHECK:")
        print(f"   • Records with missing coordinates: {quality[1]} ({quality[1]/quality[0]*100:.1f}%)")
        print(f"   • Records with missing outcomes: {quality[2]} ({quality[2]/quality[0]*100:.1f}%)")
        
        print()
        print("🎉 DATABASE VERIFICATION COMPLETED SUCCESSFULLY!")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        logger.error(f"Database verification failed: {e}")
        return False

def test_sqlite_manager():
    """Test using the SQLiteManager class"""
    try:
        from core.sqlite_manager import db_manager
        
        print("🧪 TESTING SQLiteManager CLASS")
        print("=" * 40)
        
        # Connect to database
        conn = db_manager.connect()
        cursor = conn.cursor()
        
        # Simple query
        cursor.execute("SELECT COUNT(*) FROM crime_incidents")
        count = cursor.fetchone()[0]
        print(f"Total records (via SQLiteManager): {count}")
        
        conn.close()
        
    except Exception as e:
        print(f"SQLiteManager test failed: {e}")

if __name__ == "__main__":
    verify_database()
    print("\n" + "="*50)
    test_sqlite_manager()