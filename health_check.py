from pymongo import MongoClient
import sys

try:
    client = MongoClient("mongodb://mongo:27017")
    client.admin.command("ping")
    print("MongoDB is up and running")
except Exception as e:
    print(f"Health check failed: {e}")
    sys.exit(1)
