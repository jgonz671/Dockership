from utils.logging import log_user_action
from config.db_config import DBConfig

# Initialize DBConfig
db_config = DBConfig()
db = db_config.connect()
logs_collection = db_config.get_collection("logs")


def perform_operation(username: str, operation_type: str):
    """
    Logs the operation action and updates session state for navigation.

    Args:
        username (str): The username of the current user.
        operation_type (str): The type of operation to perform (e.g., "loading", "balancing").

    Returns:
        str: The page to navigate to after the operation.
    """
    # Map operation types to log messages
    operation_map = {
        "loading": "Loading/Unloading containers",
        "balancing": "Balancing the ship's load",
    }

    # Ensure operation type is valid
    if operation_type not in operation_map:
        raise ValueError(f"Invalid operation type: {operation_type}")

    # Log the operation action
    log_user_action(
        logs_collection,
        username,
        f"User initiated the {operation_map[operation_type]} operation.",
        "",
    )

    # Return the page name for navigation
    return operation_type
