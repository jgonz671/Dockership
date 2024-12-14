from utils.logging import log_user_action
from config.db_config import DBConfig
from tasks.ship_balancer import Container, Slot
from utils.grid_utils import create_ship_grid, plotly_visualize_grid
from utils.log_manager import LogFileManager  # Import LogFileManager

# Initialize LogFileManager
db_config = DBConfig()
db = db_config.connect()
log_manager = LogFileManager(db)

def load_container_by_name(ship_grid, container_name, container_weight, target_location):
    row, col = target_location
    if ship_grid[row][col].hasContainer:
        message = f"Error: Target location [{row + 1}, {col + 1}] is already occupied."
        log_manager.write_log(message, "warning")
        return message

    if not ship_grid[row][col].available:
        message = f"Error: Target location [{row + 1}, {col + 1}] is not available for loading."
        log_manager.write_log(message, "warning")
        return message

    # Place container at the target location
    ship_grid[row][col] = Slot(
        container=Container(container_name, container_weight),
        hasContainer=True,
        available=False,
    )
    message = f"Container '{container_name}' loaded at location [{row + 1}, {col + 1}]."
    log_manager.write_log(message)
    return message


def unload_container_by_name(ship_grid, container_name):
    for row_idx, row in enumerate(ship_grid):
        for col_idx, slot in enumerate(row):
            if slot.hasContainer and slot.container.name == container_name:
                # Clear the container slot
                ship_grid[row_idx][col_idx] = Slot(container=None, hasContainer=False, available=True)
                message = f"Container '{container_name}' unloaded from location [{row_idx + 1}, {col_idx + 1}]."
                log_manager.write_log(message)
                return message, [row_idx, col_idx]
    message = f"Error: Container '{container_name}' not found on the grid."
    log_manager.write_log(message, "warning")
    return message, None


def load_containers(ship_grid, containers_and_locs):
    messages = []
    for container, location in containers_and_locs:
        messages.append(load_container_by_name(ship_grid, container.name, container.weight, location))
    log_manager.write_log(f"Loaded multiple containers: {', '.join([c[0].name for c in containers_and_locs])}.")
    return messages


def unload_containers(ship_grid, container_names):
    messages = []
    for name in container_names:
        message, _ = unload_container_by_name(ship_grid, name)
        messages.append(message)
    log_manager.write_log(f"Unloaded multiple containers: {', '.join(container_names)}.")
    return messages


def visualize_loading(ship_grid, title="Ship Loading Process"):
    plotly_visualize_grid(ship_grid, title)


def find_container_location(ship_grid, container_name):
    for row_idx, row in enumerate(ship_grid):
        for col_idx, slot in enumerate(row):
            if slot.hasContainer and slot.container.name == container_name:
                return [row_idx, col_idx]
    return None
