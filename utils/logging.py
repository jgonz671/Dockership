import pandas as pd
from pymongo.collection import Collection


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
