from utils.logging import log_user_action
from config.db_config import DBConfig
from tasks.ship_balancer import Container, Slot
from utils.grid_utils import create_ship_grid, plotly_visualize_grid
import copy

db_config = DBConfig()
db = db_config.connect()
logs_collection = db_config.get_collection("logs")

def load_container_by_name(ship_grid, container_name, container_weight, target_location):
    """
    Loads a container onto the grid at the specified location.

    Args:
        ship_grid (list): 2D grid containing Slot objects.
        container_name (str): Name of the container to be loaded.
        container_weight (int): Weight of the container to be loaded.
        target_location (list): [row, col] location for the container (0-based indexing).

    Returns:
        str: Success or error message.
    """
    row, col = target_location
    if ship_grid[row][col].hasContainer:
        return f"Error: Target location [{row + 1}, {col + 1}] is already occupied."

    if not ship_grid[row][col].available:
        return f"Error: Target location [{row + 1}, {col + 1}] is not available for loading."

    # Place container at the target location
    ship_grid[row][col] = Slot(
        container=Container(container_name, container_weight),
        hasContainer=True,
        available=False,
    )
    return f"Container '{container_name}' loaded at location [{row + 1}, {col + 1}]."


def unload_container_by_name(ship_grid, container_name):
    """
    Unloads a container from the grid based on its name.

    Args:
        ship_grid (list): 2D grid containing Slot objects.
        container_name (str): Name of the container to be unloaded.

    Returns:
        tuple: Success or error message, and the container's location if found.
    """
    for row_idx, row in enumerate(ship_grid):
        for col_idx, slot in enumerate(row):
            if slot.hasContainer and slot.container.name == container_name:
                # Clear the container slot
                ship_grid[row_idx][col_idx] = Slot(container=None, hasContainer=False, available=True)
                return f"Container '{container_name}' unloaded from location [{row_idx + 1}, {col_idx + 1}].", [row_idx, col_idx]
    return f"Error: Container '{container_name}' not found on the grid.", None


def load_containers(ship_grid, containers_and_locs):
    """
    Loads multiple containers onto the grid.

    Args:
        ship_grid (list): 2D grid containing Slot objects.
        containers_and_locs (list): List of tuples (Container, [row, col]) to load.

    Returns:
        list: Messages detailing success or failure for each container.
    """
    messages = []
    for container, location in containers_and_locs:
        messages.append(load_container_by_name(ship_grid, container.name, container.weight, location))
    return messages


def unload_containers(ship_grid, container_names):
    """
    Unloads multiple containers from the grid based on their names.

    Args:
        ship_grid (list): 2D grid containing Slot objects.
        container_names (list): List of container names to unload.

    Returns:
        list: Messages detailing success or failure for each container.
    """
    messages = []
    for name in container_names:
        message, _ = unload_container_by_name(ship_grid, name)
        messages.append(message)
    return messages


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
    load_results = load_containers(
        ship_grid,
        [
            (Container("Alpha", 1000), [0, 0]),
            (Container("Beta", 1500), [1, 1]),
        ]
    )
    for result in load_results:
        print(result)

    # Visualize grid after loading
    visualize_loading(ship_grid, title="After Loading Containers")

    # Example: Unloading containers
    print("Unloading containers...")
    unload_results = unload_containers(ship_grid, ["Alpha", "Gamma"])
    for result in unload_results:
        print(result)

    # Visualize grid after unloading
    visualize_loading(ship_grid, title="After Unloading Containers")
