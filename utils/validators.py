# utils/validators.py
import re

def validate_username(username):
    """
    Validates the username format. It must contain only alphanumeric characters, @, _, and must not be empty.
    """
    pattern = r'^[a-zA-Z0-9@_]+$'
    if re.match(pattern, username):
        return True
    return False

def validate_name(name, field_name):
    """
    Validates name fields: first and last name should only contain letters.
    """
    if field_name == "first_name" and name.strip() == "":
        return False
    if name and not name.isalpha():
        return False
    return True
