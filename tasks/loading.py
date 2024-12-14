from config.db_config import DBConfig
from tasks.ship_balancer import Container, Slot, load, unload
from utils.grid_utils import create_ship_grid, plotly_visualize_grid
import copy

db_config = DBConfig()
db = db_config.connect()
logs_collection = db_config.get_collection("logs")


def load_containers_with_balancer(ship_grid, containers_and_locs):
    """
    Loads multiple containers onto the grid using the `load` function from `ship_balancer`.

    Args:
        ship_grid (list): 2D grid containing Slot objects.
        containers_and_locs (list): List of tuples (Container, [row, col]) to load.

    Returns:
        tuple: (steps, ship_grids, messages) detailing the loading process.
    """
    steps, ship_grids = load(containers_and_locs, ship_grid)

    messages = []
    for step_list in steps:
        for step in step_list:
            messages.append(f"Loading step: {step}")

    return steps, ship_grids, messages


def unload_containers_with_balancer(ship_grid, container_names):
    """
    Unloads multiple containers from the grid using the `unload` function from `ship_balancer`.

    Args:
        ship_grid (list): 2D grid containing Slot objects.
        container_names (list): List of container names to unload.

    Returns:
        tuple: (steps, ship_grids, messages) detailing the unloading process.
    """
    container_locations = [
        find_container_location(ship_grid, name)
        for name in container_names if find_container_location(ship_grid, name) is not None
    ]

    steps, ship_grids = unload(container_locations, ship_grid)

    messages = []
    for step_list in steps:
        for step in step_list:
            messages.append(f"Unloading step: {step}")

    for name in container_names:
        if not find_container_location(ship_grid, name):
            messages.append(
                f"Error: Container '{name}' not found on the grid.")

    return steps, ship_grids, messages


def visualize_loading(ship_grid, title="Ship Loading Process"):
    """
    Visualizes the current state of the grid using Plotly.

    Args:
        ship_grid (list): 2D grid containing Slot objects.
        title (str): Title of the visualization.

    Returns:
        None
    """
    plotly_visualize_grid(ship_grid, title)


def find_container_location(ship_grid, container_name):
    """
    Finds the location of a container on the grid by its name.

    Args:
        ship_grid (list): 2D grid containing Slot objects.
        container_name (str): Name of the container to find.

    Returns:
        list: Location [row, col] of the container if found, or None.
    """
    for row_idx, row in enumerate(ship_grid):
        for col_idx, slot in enumerate(row):
            if slot.hasContainer and slot.container.name == container_name:
                return [row_idx, col_idx]
    return None


if __name__ == "__main__":
    # Example usage
    rows, cols = 8, 12
    ship_grid = create_ship_grid(rows, cols)

    # Example: Loading containers
    print("Loading containers...")
    containers_to_load = [
        (Container("Alpha", 1000), [0, 0]),
        (Container("Beta", 1500), [1, 1]),
    ]
    load_steps, load_grids, load_messages = load_containers_with_balancer(
        ship_grid, containers_to_load
    )
    for message in load_messages:
        print(message)

    # Visualize grid after loading
    visualize_loading(load_grids[-1], title="After Loading Containers")

    # Example: Unloading containers
    print("Unloading containers...")
    containers_to_unload = ["Alpha", "Gamma"]
    unload_steps, unload_grids, unload_messages = unload_containers_with_balancer(
        ship_grid, containers_to_unload
    )
    for message in unload_messages:
        print(message)

    # Visualize grid after unloading
    visualize_loading(unload_grids[-1], title="After Unloading Containers")
