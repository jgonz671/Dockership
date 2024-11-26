# config/db_config.py
"""
Handles MongoDB configuration and connection setup.
"""

import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


class DBConfig:
    """
    MongoDB configuration class.
    """

    def __init__(self):
        self.client = None
        self.db = None

    def connect(self):
        """
        Establishes a connection to the MongoDB instance.
        """
        try:
            self.client = MongoClient(os.getenv("MONGO_URI"))
            self.db = self.client[os.getenv("MONGO_DBNAME", "dockership")]
            return self.db
        except ConnectionFailure as e:
            raise RuntimeError(f"Database connection failed: {e}")

    def get_collection(self, name):
        """
        Retrieves a specific collection from the database.
        """
        if not self.db:
            raise RuntimeError(
                "Database not initialized. Call connect() first.")
        return self.db[name]
