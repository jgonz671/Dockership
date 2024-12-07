from config.db_config import DBConfig
from utils.validators import validate_username, check_user_exists
from utils.logging import log_user_action

# Initialize DBConfig
db_config = DBConfig()
db = db_config.connect()
users_collection = db_config.get_collection("users")
logs_collection = db_config.get_collection("logs")


def validate_and_check_user(username: str):
    """
    Validate the username and check if the user exists in the database.

    Args:
        username (str): The username to validate and check.

    Returns:
        tuple: (bool, str, dict or None) - A tuple containing:
               - Whether the validation and check were successful.
               - An error message if unsuccessful.
               - The user document if found, or None otherwise.
    """
    # Validate the username
    is_valid, error_message = validate_username(username)
    if not is_valid:
        return False, error_message, None

    # Check if the user exists
    user = check_user_exists(username)
    if not user:
        return False, "Username not found. Please register.", None

    # Log the user action
    log_user_action(logs_collection, username, "Login", "User logged in successfully.")
    
    return True, "", user
