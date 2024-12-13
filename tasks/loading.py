from utils.logging import log_user_action
from config.db_config import DBConfig
from utils.visualizer import plotly_visualize_grid
from tasks.balancing import Container, Slot
import copy

# Initialize database connection
db_config = DBConfig()
db = db_config.connect()
logs_collection = db_config.get_collection("logs")

def optimize_load_unload(manifest, unload_list, load_list):
    """
    Optimizes the loading/unloading sequence to minimize time and crane idle.

    Args:
        manifest (list): Current ship grid layout with Slot objects.
        unload_list (list): Containers to unload.
        load_list (list): Containers to load.

    Returns:
        list: A sequence of operations (load/unload) with intermediate grid states.
    """
    operations = []
    unload_queue = list(unload_list)
    load_queue = list(load_list)
    grid_states = []

    while unload_queue or load_queue:
        # Prioritize unloading
        if unload_queue:
            container = unload_queue.pop(0)
            for i, row in enumerate(manifest):
                for j, slot in enumerate(row):
                    if slot.has_container and slot.container.name == container:
                        operations.append({
                            "action": "UNLOAD",
                            "description": f"Unloaded container {container} from position [{i}, {j}]",
                            "grid": plotly_visualize_grid(copy.deepcopy(manifest), title=f"Unloading {container} Step")
                        })
                        slot.container = None
                        slot.has_container = False
                        slot.available = True
                        grid_states.append(plotly_visualize_grid(copy.deepcopy(manifest), title=f"State After Unloading {container}"))
                        break
                else:
                    continue
                break

        # Intertwine loading
        if load_queue:
            container = load_queue.pop(0)
            for i, row in enumerate(manifest):
                for j, slot in enumerate(row):
                    if slot.available:
                        slot.container = Container(name=container, weight=0)  # Default weight as 0
                        slot.has_container = True
                        slot.available = False
                        operations.append({
                            "action": "LOAD",
                            "description": f"Loaded container {container} to position [{i}, {j}]",
                            "grid": plotly_visualize_grid(copy.deepcopy(manifest), title=f"Loading {container} Step")
                        })
                        grid_states.append(plotly_visualize_grid(copy.deepcopy(manifest), title=f"State After Loading {container}"))
                        break
                else:
                    continue
                break

    return operations, grid_states