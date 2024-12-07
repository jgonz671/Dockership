# auth/login.py
import os
from dotenv import load_dotenv
from pymongo import MongoClient
import pandas as pd

# Load environment variables
load_dotenv()

# MongoDB connection
mongo_uri = os.getenv("MONGO_URI")
database_name = os.getenv("MONGO_DBNAME", "dockership")

client = MongoClient(mongo_uri)
db = client[database_name]
users_collection = db.users
log_collection = db.logs

def check_user_exists(username: str):
    """
    Check if a user with the given username exists in the database.
    
    Args:
        username (str): The username to check.
        
    Returns:
        dict or None: User document if found, None otherwise.
    """
    return users_collection.find_one({"username": username})

def log_user_action(username: str, action: str):
    """
    Log a user's action to the log collection.
    
    Args:
        username (str): The username of the user.
        action (str): The action performed by the user.
    """
    log_entry = {
        'user': username,
        'timestamp': pd.Timestamp.now(),
        'action': action
    }
    log_collection.insert_one(log_entry)
