import os
from pymongo import MongoClient, errors
from pymongo.collection import Collection
from datetime import datetime


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

            # Ensure critical collections exist and initialize data
            self._initialize_collections()

            return self.db
        except errors.ConnectionFailure as e:
            raise RuntimeError(f"Database connection failed: {e}")
        except ValueError as e:
            raise RuntimeError(f"Environment error: {e}")

    def _initialize_collections(self):
        """
        Ensures required collections exist and inserts sample data where applicable.
        """
        # Required collections with optional sample data
        collections_with_samples = {
            "users": [
                {"first_name": "John", "last_name": "Doe", "username": "johndoe"},
                {"first_name": "Jane", "last_name": "Smith", "username": "janesmith"}
            ],
            "logs": [
                {"username": "system", "timestamp": datetime.utcnow(), "action": "Database initialized", "notes": "Initial setup completed."}
            ],
            "manifests": [
                {"username": "system", "incoming_file": "manifest_inbound.txt", "outgoing_file": "manifest_outbound.txt"}
            ],
            "logfile": [
                {"timestamp": datetime.utcnow(), "message": "Logfile initialized."}
            ],
            "ship_state": [
                {"grid": [
                    [{"has_container": True, "container": {"name": "Alpha", "weight": 1000}, "available": False}],
                    [{"has_container": False, "container": None, "available": True}]
                ],
                "updated_at": datetime.utcnow(),
                "notes": "Initial ship grid setup."}
            ],
            "operations": [
                {"operation_id": "OP001", "type": "load", "container": {"name": "Alpha", "weight": 1000},
                 "location": {"row": 0, "col": 0}, "timestamp": datetime.utcnow(), "performed_by": "system"}
            ]
        }

        # Initialize collections
        for collection_name, sample_data in collections_with_samples.items():
            if collection_name not in self.db.list_collection_names():
                self.db.create_collection(collection_name)
                print(f"✅ Created '{collection_name}' collection.")

                # Insert sample data
                if sample_data:
                    self.db[collection_name].insert_many(sample_data)
                    print(f"🔹 Inserted sample data into '{collection_name}' collection.")
            else:
                print(f"🔹 '{collection_name}' collection already exists.")

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
