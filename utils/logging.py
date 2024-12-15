import pandas as pd
from pymongo.collection import Collection
from config.db_config import DBConfig
from datetime import datetime, timedelta
import os

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

    Args:
        username (str): Username performing the action.
        action (str): The action performed.
        notes (str, optional): Additional details about the action.
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
        logs = logs_collection.find(
            {"timestamp": {"$gte": one_year_ago}}).sort("timestamp", 1)
        return list(logs)
    except Exception as e:
        print(f"❌ Failed to retrieve logs from the last year: {e}")
        return []


def format_timestamp(timestamp):
    """
    Converts a timestamp into the format: 'Month Day(st/nd/rd/th) Year: HH:MM'

    Args:
        timestamp (datetime): The original datetime object.

    Returns:
        str: Formatted timestamp string.
    """
    suffixes = {1: "st", 2: "nd", 3: "rd"}
    day = timestamp.day
    suffix = suffixes.get(day if day < 20 else day % 10, "th")
    formatted_time = timestamp.strftime(f"%B {day}{suffix} %Y: %H:%M")
    return formatted_time


def format_logs_to_string(logs):
    """
    Converts logs into a list of formatted strings.

    Args:
        logs (list): A list of log entries from MongoDB.

    Returns:
        list: A list of formatted strings.
    """
    formatted_logs = []
    for log in logs:
        timestamp = log.get("timestamp", datetime.now())
        formatted_timestamp = format_timestamp(timestamp)
        username = log.get("username", "Unknown")
        action = log.get("action", "No Action")
        notes = log.get("notes", "No Message")
        formatted_logs.append(
            f"{formatted_timestamp} : {username} : {action} : {notes}")
    return formatted_logs


def create_logs_file():
    """
    Generates a .txt file containing all logs from the last year.

    Returns:
        str: Path to the generated .txt file.
    """
    try:
        logs = get_logs_last_year()
        if not logs:
            print("No logs found for the last year.")
            return None

        formatted_logs = format_logs_to_string(logs)

        # Define file name and path
        file_name = "logs.txt"
        file_path = os.path.join(os.getcwd(), file_name)

        # Write logs to file
        with open(file_path, "w", encoding="utf-8") as file:
            for log_entry in formatted_logs:
                file.write(log_entry + "\n")

        print(f"✅ Logs file created successfully: {file_path}")
        return file_path
    except Exception as e:
        print(f"❌ Failed to create logs file: {e}")
        return None
