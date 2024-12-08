from utils.logging import log_user_action
from config.db_config import DBConfig
import copy

# Initialize database connection
db_config = DBConfig()
db = db_config.connect()
logs_collection = db_config.get_collection("logs")


def optimize_load_unload(manifest, unload_list, load_list):
    """
    Optimizes the loading/unloading sequence to minimize time and crane idle.

    Args:
        manifest (list): Current ship layout.
        unload_list (list): Containers to unload.
        load_list (list): Containers to load.

    Returns:
        list: A sequence of operations (load/unload) as a list of steps, including intermediate grid states.
    """
    operations = []
    unload_queue = list(unload_list)
    load_queue = list(load_list)

    while unload_queue or load_queue:
        # Prioritize unloading to keep the ship clear
        if unload_queue:
            container = unload_queue.pop(0)
            for i, row in enumerate(manifest):
                for j, slot in enumerate(row):
                    if slot == container:
                        operations.append({
                            "action": "UNLOAD",
                            "description": f"Unloaded container {container} from position [{i}, {j}]",
                            "grid": copy.deepcopy(manifest)
                        })
                        manifest[i][j] = "UNUSED"
                        log_user_action(
                            logs_collection,
                            "system",
                            f"Unloaded container {container} from position [{i}, {j}]"
                        )
                        break
                else:
                    continue
                break

        # Intertwine loading
        if load_queue:
            container = load_queue.pop(0)
            for i, row in enumerate(manifest):
                for j, slot in enumerate(row):
                    if slot == "UNUSED":
                        operations.append({
                            "action": "LOAD",
                            "description": f"Loaded container {container} to position [{i}, {j}]",
                            "grid": copy.deepcopy(manifest),
                            "container": container,  # Add container name for tracking
                        })
                        manifest[i][j] = container
                        log_user_action(
                            logs_collection,
                            "system",
                            f"Loaded container {container} to position [{i}, {j}]"
                        )
                        break
                else:
                    continue
                break

    return operations


def execute_operations(manifest, operations):
    """
    Executes the sequence of operations on the manifest.

    Args:
        manifest (list): Current ship layout.
        operations (list): List of operations (LOAD/UNLOAD) to execute.

    Returns:
        list: Updated ship manifest after all operations.
    """
    for operation in operations:
        action = operation["action"]
        container = operation.get("container")  # Fetch container name for loading
        grid = operation["grid"]  # Update to the operation's grid state
        i, j = operation["grid"]

        if action == "LOAD":
            manifest[i][j] = container
        elif action == "UNLOAD":
            manifest[i][j] = "UNUSED"

    return manifest
