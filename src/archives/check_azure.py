#!/usr/bin/env python3
"""Check Azure connection setup"""

from dotenv import load_dotenv
import os

load_dotenv()

connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

print("🔍 Azure Connection Check")
print("=" * 40)
print(f"Connection string exists: {bool(connection_string)}")
print(f"Length: {len(connection_string) if connection_string else 0}")
if connection_string:
    # Show first part for verification (don't print full key)
    account_name = connection_string.split('AccountName=')[1].split(';')[0] if 'AccountName=' in connection_string else 'Not found'
    print(f"Account name: {account_name}")
    print("✅ Connection string looks good!")
else:
    print("❌ No connection string found!")
    print("\nTo fix:")
    print("1. Get connection string from Azure Portal → Storage Account → Access Keys")
    print("2. Set environment variable or add to .env file")