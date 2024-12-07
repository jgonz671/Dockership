# utils/validators.py
import re
from config.db_config import DBConfig

# Initialize DBConfig
db_config = DBConfig()
db = db_config.connect()
users_collection = db_config.get_collection("users")


def check_user_exists(username: str):
    """
    Check if a user with the given username exists in the database.

    Args:
        username (str): The username to check.

    Returns:
        dict or None: User document if found, None otherwise.
    """
    return users_collection.find_one({"username": username})


def validate_username(username):
    """
    Validates the username format. It must contain only alphanumeric characters, @, _, and must not be empty.
    
    Args:
        username (str): The username to validate.

    Returns:
        tuple: (bool, str) - A tuple containing whether the username is valid and an error message if invalid.
    """
    if not username.strip():
        return False, "Username cannot be empty."
    if len(username) > 30:
        return False, "Username cannot exceed 30 characters."
    pattern = r'^[a-zA-Z0-9@_]+$'
    if not re.match(pattern, username):
        return False, "Username can only contain letters, numbers, @, and _."
    return True, ""

def validate_name(name, field_name):
    """
    Validates name fields: first and last name should only contain letters.
    
    Args:
        name (str): The name to validate.
        field_name (str): The name of the field (e.g., "first_name", "last_name").

    Returns:
        tuple: (bool, str) - A tuple containing whether the name is valid and an error message if invalid.
    """
    if field_name == "first_name" and not name.strip():
        return False, "First name is required."
    if len(name) > 50:
        return False, f"{field_name.replace('_', ' ').capitalize()} cannot exceed 50 characters."
    if not name.isalpha():
        return False, f"{field_name.replace('_', ' ').capitalize()} can only contain letters."
    return True, ""

def validate_required_field(field, field_name):
    """
    Validates that a required field is not empty.
    
    Args:
        field (str): The value of the field to validate.
        field_name (str): The name of the field.

    Returns:
        tuple: (bool, str) - A tuple containing whether the field is valid and an error message if invalid.
    """
    if not field.strip():
        return False, f"{field_name} is required."
    return True, ""

def validate_file_content(file_content):
    """
    Validates the content of the uploaded file.

    Args:
        file_content (str): The content of the uploaded file.

    Returns:
        tuple: (bool, str) - A tuple containing whether the content is valid and an error message if invalid.
    """
    if not file_content.strip():
        return False, "The uploaded file is empty."
    if len(file_content) > 10000:  # Arbitrary limit for demonstration
        return False, "The uploaded file exceeds the allowed size."
    return True, ""
