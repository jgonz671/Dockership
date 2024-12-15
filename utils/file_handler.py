from utils.logging import log_action


def process_file_content(file_content):
    """
    Processes the uploaded file content for further use.

    Args:
        file_content (str): The content of the uploaded file.

    Returns:
        list: A list of lines from the file content.
    """
    return file_content.splitlines()


def log_file_upload(username, filename):
    """
    Logs the file upload action.

    Args:
        logs_collection: MongoDB collection for logs.
        username: The username of the user uploading the file.
        filename: The name of the uploaded file.
    """
    log_action(
        username=username,
        action="UPLOAD_FILE",
        notes=f"{username} uploaded file: {filename}",
    )


def log_proceed_to_operations(username):
    """
    Logs the action when the user proceeds to operations.

    Args:
        logs_collection: MongoDB collection for logs.
        username: The username of the user proceeding to operations.
    """
    log_action(
        username=username,
        action="PROCEED_TO_OPERATIONS",
        notes=f"{username} proceeded to operations.",
    )
