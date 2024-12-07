from config.db_config import DBConfig
from utils.validators import check_user_exists
from utils.logging import log_user_action

# Initialize DBConfig
db_config = DBConfig()
db = db_config.connect()
users_collection = db_config.get_collection("users")
logs_collection = db_config.get_collection("logs")


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
    if check_user_exists(username):
        return False  # Username already exists

    # Capitalize the names
    first_name = first_name.capitalize()
    last_name = last_name.capitalize() if last_name else ''

    # Insert user into the users collection
    users_collection.insert_one({
        "first_name": first_name,
        "last_name": last_name,
        "username": username,
    })

    # Log registration action
    log_user_action(logs_collection, username, "Registration",
                    "User registered successfully.")

    return True
