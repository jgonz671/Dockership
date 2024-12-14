from utils.logging import log_user_action
from config.db_config import DBConfig
from utils.grid_utils import plotly_visualize_grid
from tasks.ship_balancer import Container, Slot

# Initialize database connection
db_config = DBConfig()
db = db_config.connect()
logs_collection = db_config.get_collection("logs")

def optimize_load_unload(manifest, unload_list, load_list):
    """
    Optimizes the loading/unloading sequence to minimize time and crane idle.

    Args:
        manifest (list): Current ship grid layout with Slot objects.
        unload_list (list): Containers to unload (list of container names).
        load_list (list): Containers to load (list of tuples: [(name, weight)]).

    Returns:
        tuple: A sequence of operations (load/unload) and intermediate grid states.
    """
    # Validate that manifest is initialized correctly with Slot objects
    if not all(all(isinstance(slot, Slot) for slot in row) for row in manifest):
        raise ValueError("Manifest must be a 2D grid of Slot objects.")

    operations = []
    unload_queue = list(unload_list)
    load_queue = list(load_list)  # Expecting [(name, weight)]
    grid_states = []

    unload_counter = 0  # Counter for unique unload keys
    load_counter = 0  # Counter for unique load keys

    while unload_queue or load_queue:
        # Prioritize unloading
        if unload_queue:
            container_name = unload_queue.pop(0)
            container_found = False
            for i, row in enumerate(manifest):
                for j, slot in enumerate(row):
                    if slot.hasContainer and slot.container and slot.container.name == container_name:
                        operations.append({
                            "action": "UNLOAD",
                            "description": f"Unloaded container {container_name} from position [{i}, {j}]",
                            "grid": plotly_visualize_grid(
                                copy.deepcopy(manifest),
                                title=f"Unloading {container_name} Step",
                                key=f"unloading_{container_name}_{unload_counter}"
                            )
                        })
                        # Update the Slot to reflect unloading
                        slot.container = None
                        slot.hasContainer = False
                        slot.available = True

                        # Visualize the updated state
                        grid_states.append(
                            plotly_visualize_grid(
                                copy.deepcopy(manifest),
                                title=f"State After Unloading {container_name}",
                                key=f"state_after_unloading_{container_name}_{unload_counter}"
                            )
                        )
                        unload_counter += 1
                        container_found = True
                        break
                if container_found:
                    break
            if not container_found:
                operations.append({
                    "action": "ERROR",
                    "description": f"Container {container_name} not found in manifest"
                })

        # Intertwine loading
        if load_queue:
            container_name, container_weight = load_queue.pop(0)
            slot_found = False
            for i, row in enumerate(manifest):
                for j, slot in enumerate(row):
                    if slot.available:
                        # Update the Slot with the new container
                        slot.container = Container(name=container_name, weight=container_weight)
                        slot.hasContainer = True
                        slot.available = False
                        operations.append({
                            "action": "LOAD",
                            "description": f"Loaded container {container_name} (Weight: {container_weight}) to position [{i}, {j}]",
                            "grid": plotly_visualize_grid(
                                copy.deepcopy(manifest),
                                title=f"Loading {container_name} Step",
                                key=f"loading_{container_name}_{load_counter}"
                            )
                        })
                        # Visualize the updated state
                        grid_states.append(
                            plotly_visualize_grid(
                                copy.deepcopy(manifest),
                                title=f"State After Loading {container_name}",
                                key=f"state_after_loading_{container_name}_{load_counter}"
                            )
                        )
                        load_counter += 1
                        slot_found = True
                        break
                if slot_found:
                    break
            if not slot_found:
                operations.append({
                    "action": "ERROR",
                    "description": f"No available slot for container {container_name}"
                })

    return operations, grid_states
