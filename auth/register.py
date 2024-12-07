# auth/register.py
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from utils.validators import validate_username, validate_name

# Load environment variables
load_dotenv()

# MongoDB connection
mongo_uri = os.getenv("MONGO_URI")
database_name = os.getenv("MONGO_DBNAME", "dockership")

client = MongoClient(mongo_uri)
db = client[database_name]
users_collection = db.users

def register_user(first_name: str, last_name: str, username: str):
    """
    Register a new user by adding their details to the users collection.
    
    Args:
        first_name (str): The first name of the user.
        last_name (str): The last name of the user.
        username (str): The username of the user.
        
    Returns:
        bool: True if registration is successful, False otherwise.
    """
    if users_collection.find_one({"username": username}):
        return False  # Username already exists
    
    # Capitalize the names
    first_name = first_name.capitalize()
    last_name = last_name.capitalize() if last_name else ''
    
    users_collection.insert_one({
        'first_name': first_name,
        'last_name': last_name,
        'username': username
    })
    return True
