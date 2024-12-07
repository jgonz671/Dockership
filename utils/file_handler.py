# Dockership/tasks/file_handler.py

from utils.validators import validate_file_content

def process_file(file_content):
    """
    Processes the uploaded file content.

    Args:
        file_content (str): The content of the uploaded file.

    Returns:
        dict: A dictionary containing processed data or metadata.
    """
    # Example of processing: Parse lines into a list
    lines = file_content.splitlines()
    processed_data = {
        "line_count": len(lines),
        "first_10_lines": lines[:10]
    }
    return processed_data
