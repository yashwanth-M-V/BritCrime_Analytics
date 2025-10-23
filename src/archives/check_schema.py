#!/usr/bin/env python3
"""Check the actual database schema"""

import sqlite3
import pandas as pd

def check_schema():
    print(" CHECKING DATABASE SCHEMA")
    print("=" * 50)
    
    conn = sqlite3.connect("data/crime_data.db")
    cursor = conn.cursor()
    
    # Check crime_incidents table structure
    print(" crime_incidents table columns:")
    cursor.execute("PRAGMA table_info(crime_incidents)")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    print("\n Sample data from crime_incidents:")
    cursor.execute("SELECT * FROM crime_incidents LIMIT 1")
    sample = cursor.fetchone()
    if sample:
        column_names = [description[0] for description in cursor.description]
        for name, value in zip(column_names, sample):
            print(f"  - {name}: {value}")
    
    print("\n police_forces table:")
    cursor.execute("SELECT * FROM police_forces")
    forces = cursor.fetchall()
    for force in forces:
        print(f"  - {force}")
    
    conn.close()

if __name__ == "__main__":
    check_schema()