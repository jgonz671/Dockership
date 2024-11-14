# modules/db_config.py
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_db():
    try:
        # Connect to MongoDB using the complete URI from environment variable
        client = MongoClient(os.getenv('MONGO_URI'))
        # Access the specific database
        return client[os.getenv('MONGO_DBNAME', 'dockership')]
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        # Consider re-raising the exception or handling it to maintain app stability
        raise
