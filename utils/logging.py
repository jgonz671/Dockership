import pandas as pd
from pymongo.collection import Collection
from config.db_config import DBConfig
from datetime import datetime, timedelta

# Initialize DBConfig to access collections
db_config = DBConfig()
db = db_config.connect()
logs_collection = db_config.get_collection("logs")


def log_user_action(logs_collection: Collection, username: str, action: str, notes: str = None):
    """
    Logs a user's action in the logs collection.

    Args:
        logs_collection (Collection): MongoDB collection for logs.
        username (str): Username performing the action.
        action (str): The action performed.
        notes (str, optional): Additional details about the action.
    """
    log_entry = {
        "username": username,
        "timestamp": pd.Timestamp.now(),
        "action": action,
        "notes": notes,
    }
    logs_collection.insert_one(log_entry)


def log_action(username: str, action: str, notes: str = None):
    """
    Wrapper function for logging user actions in the logs collection.

    This function simplifies logging by automatically fetching the logs collection.

    Args:
        username (str): Username performing the action.
        action (str): The action performed.
        notes (str, optional): Additional details about the action.

    Example:
        log_action("johndoe", "File Upload", "Uploaded manifest file")
    """
    try:
        log_user_action(logs_collection, username, action, notes)
    except Exception as e:
        print(f"❌ Failed to log action: {e}")


def get_logs_last_year():
    """
    Retrieves all logs from the logs collection added in the last year.

    Returns:
        list: A list of logs added in the last year.
    """
    try:
        one_year_ago = datetime.now() - timedelta(days=365)
        logs = logs_collection.find({"timestamp": {"$gte": one_year_ago}}).sort("timestamp", 1)
        return list(logs)
    except Exception as e:
        print(f"❌ Failed to retrieve logs from the last year: {e}")
        return []