import os
from datetime import datetime
from pymongo.collection import Collection
from pymongo import MongoClient

class LogFileManager:
    """
    Manages logging to MongoDB and a plain text file.
    """
    def __init__(self, db: Collection, log_dir="logs"):
        """
        Initializes the LogFileManager.

        Args:
            db (Collection): MongoDB collection for storing logs.
            log_dir (str): Directory where log files will be stored.
        """
        self.db = db
        self.log_dir = log_dir
        self.log_file_path = self._get_log_file_path()

        # Ensure log directory exists
        os.makedirs(self.log_dir, exist_ok=True)

    def _get_log_file_path(self):
        """
        Generates a log file path dynamically based on the current year.
        """
        year = datetime.now().year
        filename = f"KeoghsPort{year}.txt"
        return os.path.join(self.log_dir, filename)

    def log(self, message: str, log_type: str = "info"):
        """
        Logs a message to MongoDB and a text file.

        Args:
            message (str): The message to log.
            log_type (str): The type of log (e.g., 'info', 'error', 'warning').
        """
        timestamp = datetime.utcnow()

        # MongoDB log entry
        log_entry = {
            "timestamp": timestamp,
            "message": message,
            "type": log_type
        }
        self.db.insert_one(log_entry)

        # File log entry
        log_line = f"{timestamp.strftime('%Y-%m-%d %H:%M:%S')} - [{log_type.upper()}] {message}\n"
        with open(self.log_file_path, "a", encoding="utf-8") as file:
            file.write(log_line)

        # Optional: Print to console for debugging
        print(log_line.strip())

    def get_log_file_path(self):
        """Returns the current log file path."""
        return self.log_file_path
