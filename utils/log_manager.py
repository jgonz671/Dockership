import os
from datetime import datetime
from pymongo import MongoClient

class LogFileManager:
    def __init__(self, db, base_dir="logs"):
        self.log_collection = db["logs"]
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)
        self.log_file_name = f"KeoghsPort{datetime.now().year}.txt"
        self.log_file_path = os.path.join(self.base_dir, self.log_file_name)

    def write_log(self, message):
        timestamp = datetime.now()
        timestamp_str = timestamp.strftime("%B %d %Y, %H:%M:%S")
        
        # Write to the log file
        log_message = f"{timestamp_str} - {message}\n"
        with open(self.log_file_path, "a", encoding="utf-8") as log_file:
            log_file.write(log_message)
        
        # Insert into the database
        log_entry = {
            "timestamp": timestamp,
            "message": message,
        }
        self.log_collection.insert_one(log_entry)


    def read_logs(self):
        if os.path.exists(self.log_file_path):
            with open(self.log_file_path, "r", encoding="utf-8") as log_file:
                return log_file.read()
        return "No logs available yet."

    def get_logs_from_db(self, limit=50):
        return list(self.log_collection.find().sort("timestamp", -1).limit(limit))