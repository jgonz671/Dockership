# Dockership/utils/file_handler.py

from utils.validators import validate_file_content
from utils.logging import log_user_action


def process_file(file_content):
    """
    Processes the uploaded file content.

    Args:
        file_content (str): The content of the uploaded file.

    Returns:
        dict: A dictionary containing processed data or metadata.
    """
    lines = file_content.splitlines()
    processed_data = {
        "line_count": len(lines),
        "first_10_lines": lines[:10],
    }
    return processed_data


def log_file_upload(logs_collection, username, filename):
    """
    Logs the file upload action.

    Args:
        logs_collection: MongoDB collection for logs.
        username: The username of the user uploading the file.
        filename: The name of the uploaded file.
    """
    log_user_action(
        logs_collection,
        username,
        f"User uploaded file: {filename}",
        "",
    )


def log_proceed_to_operations(logs_collection, username):
    """
    Logs the action when the user proceeds to operations.

    Args:
        logs_collection: MongoDB collection for logs.
        username: The username of the user proceeding to operations.
    """
    log_user_action(
        logs_collection,
        username,
        "User clicked to proceed to operations.",
        "",
    )
