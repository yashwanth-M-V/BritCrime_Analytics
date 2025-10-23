#!/usr/bin/env python3
"""Complete Azure test with corrected schema"""

from utlis.azure_client import azure_client
import time

def test_azure_complete():
    print("🧪 COMPLETE Azure Test - Corrected Schema")
    print("=" * 60)
    
    # Test connection
    status = azure_client.get_upload_status()
    print(f"📡 Azure Status: {status['status']}")
    print(f"📁 Container: {status.get('container', 'N/A')}")
    print(f"📊 Total files: {status.get('total_files', 0)}")
    
    # Test uploads
    print("\n📤 TESTING UPLOADS")
    print("-" * 30)
    
    print("1. Uploading SQLite database...")
    db_success = azure_client.upload_sqlite_database()
    print(f"   ✅ Database upload: {'SUCCESS' if db_success else 'FAILED'}")
    
    time.sleep(2)
    
    print("2. Uploading Streamlit datasets...")
    data_success = azure_client.upload_streamlit_data()
    print(f"   ✅ Streamlit data: {'SUCCESS' if data_success else 'FAILED'}")
    
    # Test downloads
    print("\n📥 TESTING DOWNLOADS") 
    print("-" * 30)
    
    test_datasets = [
        "crime_incidents", 
        "crime_summary", 
        "crime_trends",
        "crime_locations",
        "crime_severity"
    ]
    
    all_downloads_success = True
    
    for dataset in test_datasets:
        try:
            df = azure_client.download_streamlit_data(dataset)
            if not df.empty:
                print(f"   📈 {dataset}: {len(df):,} records - ✅ SUCCESS")
                print(f"      Columns: {list(df.columns)[:3]}...")  # Show first 3 columns
            else:
                print(f"   📈 {dataset}: 0 records - ⚠️ EMPTY")
                all_downloads_success = False
        except Exception as e:
            print(f"   📈 {dataset}: ❌ FAILED - {e}")
            all_downloads_success = False
    
    # Final status
    print("\n" + "=" * 60)
    final_status = azure_client.get_upload_status()
    print("🎯 FINAL AZURE STATUS")
    print("-" * 30)
    print(f"📦 Total files in Azure: {final_status.get('total_files', 0)}")
    
    if 'blobs' in final_status:
        streamlit_files = [blob for blob in final_status['blobs'] if 'streamlit' in blob]
        print(f"📊 Streamlit datasets: {len(streamlit_files)}")
        for blob in streamlit_files:
            print(f"   📄 {blob}")
    
    success = db_success and data_success and all_downloads_success
    print(f"\n🎉 {'ALL TESTS PASSED! 🚀 Ready for Streamlit!' if success else 'SOME TESTS FAILED! ⚠️'}")
    
    return success

if __name__ == "__main__":
    success = test_azure_complete()
    exit(0 if success else 1)