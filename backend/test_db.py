from database import get_scholarship_collection

try:
    collection = get_scholarship_collection()
    # Try inserting a test document
    result = collection.insert_one({"test": "connection_working"})
    print("✅ MongoDB Connected Successfully!")
    print(f"Inserted ID: {result.inserted_id}")
    
    # Delete the test document
    collection.delete_one({"_id": result.inserted_id})
    print("✅ Test document cleaned up.")
    
except Exception as e:
    print(f"❌ Connection Failed: {e}")