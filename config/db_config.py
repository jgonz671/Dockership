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
        Establishes a connection to the MongoDB instance and ensures the database exists.
        """
        try:
            # Fetch the MongoDB URI from environment variables
            mongo_uri = os.getenv("MONGO_URI")
            if not mongo_uri:
                raise ValueError("MONGO_URI is not set in the environment variables.")

            # Connect to MongoDB using the Atlas URI
            self.client = MongoClient(mongo_uri)
            self.db = self.client[os.getenv("MONGO_DBNAME", "dockership")]

            # Ensure critical collections exist
            self._initialize_collections()

            return self.db
        except ConnectionFailure as e:
            raise RuntimeError(f"Database connection failed: {e}")
        except ValueError as e:
            raise RuntimeError(f"Environment error: {e}")

    def _initialize_collections(self):
        """
        Ensures that required collections exist in the database.
        """
        required_collections = ["users", "logs", "operations"]
        existing_collections = self.db.list_collection_names()

        for collection in required_collections:
            if collection not in existing_collections:
                self.db.create_collection(collection)

    def get_collection(self, name):
        """
        Retrieves a specific collection from the database.
        """
        if not self.db:
            raise RuntimeError("Database not initialized. Call connect() first.")
        return self.db[name]

    def check_connection(self):
        """
        Checks if the connection to MongoDB is successful.
        Returns True if the connection is successful, False otherwise.
        """
        try:
            self.client.admin.command("ping")
            print("✅ MongoDB connection successful.")
            return True
        except Exception as e:
            print(f"❌ MongoDB connection check failed: {e}")
            return False
