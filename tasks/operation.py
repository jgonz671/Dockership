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
    # Log the action
    log_user_action(
        logs_collection,
        username,
        f"{operation_type.capitalize()} Operation",
        f"User initiated the {operation_type} operation.",
    )

    # Return the page name for navigation
    return operation_type
