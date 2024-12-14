import os
from pymongo import MongoClient, errors
from pymongo.collection import Collection


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
                raise ValueError(
                    "MONGO_URI is not set in the environment variables.")

            # Connect to MongoDB
            self.client = MongoClient(mongo_uri)
            self.db = self.client[os.getenv("MONGO_DBNAME", "dockership")]

            # Ensure critical collections exist
            self._initialize_collections()

            return self.db
        except errors.ConnectionFailure as e:
            raise RuntimeError(f"Database connection failed: {e}")
        except ValueError as e:
            raise RuntimeError(f"Environment error: {e}")

    def _initialize_collections(self):
        """
        Ensures required collections exist and validates their schemas.
        """
        schemas = {
            "users": {
                "first_name": {"type": "string", "required": True, "max_length": 50},
                "last_name": {"type": "string", "required": False, "max_length": 50},
                "username": {"type": "string", "required": True, "unique": True, "max_length": 30},
            },
            "logs": {
                # FK to users
                "username": {"type": "string", "required": True},
                "timestamp": {"type": "datetime", "required": True},
                "action": {"type": "string", "required": True},
                "notes": {"type": "string", "required": False},
            },
            "manifests": {
                # FK to users
                "username": {"type": "string", "required": True},
                "incoming_file": {"type": "string", "required": True},
                "outgoing_file": {"type": "string", "required": True},
            },
            "logfile": {
                "timestamp": {"type": "datetime", "required": True},
                "message": {"type": "string", "required": True},
            },
        }

        for collection, schema in schemas.items():
            self._ensure_collection_schema(collection, schema)

    def _ensure_collection_schema(self, collection_name, schema):
        """
        Ensures a collection exists and applies the schema (simulation).
        """
        collection = self.db[collection_name]

        # Add schema validation logic here if using MongoDB with validation rules (e.g., JSON Schema)

    def get_collection(self, name) -> Collection:
        """
        Retrieves a specific collection from the database.
        """
        if self.db is None:  # Compare explicitly with None
            raise RuntimeError(
                "Database not initialized. Call connect() first.")
        return self.db[name]

    def check_connection(self):
        """
        Checks if the connection to MongoDB is successful.
        """
        try:
            self.client.admin.command("ping")
            print("✅ MongoDB connection successful.")
            return True
        except Exception as e:
            print(f"❌ MongoDB connection check failed: {e}")
            return False
