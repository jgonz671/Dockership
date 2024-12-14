from tasks.ship_balancer import Container, Slot, manhattan_distance


def find_next_available_position(ship_grid):
    """
    Finds the next available position on the grid for loading, starting from the top-left.
    Ensures no floating containers.

    Args:
        ship_grid (list): 2D grid of slots.

    Returns:
        tuple: (row, col) of the next available position or (-1, -1) if no slots are available.
    """
    for row_idx, row in enumerate(ship_grid):
        for col_idx, slot in enumerate(row):
            if slot.available:
                # Check if the position is supported (row == 0 or a container is below)
                if row_idx == 0 or ship_grid[row_idx - 1][col_idx].hasContainer:
                    return row_idx, col_idx
    return -1, -1  # No available slots


def find_nearest_container(ship_grid, origin=(0, 0)):
    """
    Finds the nearest container to the given origin for unloading.
    Ensures there are no containers above the target.

    Args:
        ship_grid (list): 2D grid of slots.
        origin (tuple): (row, col) from where to search for the nearest container.

    Returns:
        tuple: (row, col) of the nearest container or (-1, -1) if no containers are found.
    """
    min_distance = float("inf")
    nearest_position = (-1, -1)

    for row_idx, row in enumerate(ship_grid):
        for col_idx, slot in enumerate(row):
            if slot.hasContainer:
                # Check if no container is above this one
                if row_idx < len(ship_grid) - 1 and ship_grid[row_idx + 1][col_idx].hasContainer:
                    continue  # Skip this slot because it has a container above

                distance = manhattan_distance(origin, (row_idx, col_idx))
                if distance < min_distance:
                    min_distance = distance
                    nearest_position = (row_idx, col_idx)

    return nearest_position


def load_containers(ship_grid, container_names):
    """
    Loads multiple containers onto the grid in the first available positions.
    Ensures no floating containers.

    Args:
        ship_grid (list): 2D grid of slots.
        container_names (list): List of container names to be loaded.

    Returns:
        list: Messages indicating the result of each load operation.
    """
    messages = []
    default_weight = 100  # Assign a default weight

    for container_name in container_names:
        target_position = find_next_available_position(ship_grid)

        if target_position == (-1, -1):
            messages.append(f"Error: No available slots for container '{container_name}'.")
            continue

        row, col = target_position

        # Place the container at the target position with default weight
        ship_grid[row][col] = Slot(
            container=Container(name=container_name, weight=default_weight),
            hasContainer=True,
            available=False,
        )
        messages.append(f"Container '{container_name}' loaded at [{row + 1}, {col + 1}].")
    return messages



def unload_containers(ship_grid, container_names):
    """
    Unloads multiple containers by name from the grid, starting with the nearest to the origin.
    Ensures there are no containers above the target.

    Args:
        ship_grid (list): 2D grid of slots.
        container_names (list): List of container names to be unloaded.

    Returns:
        list: Messages indicating the result of each unload operation.
    """
    origin = (0, 0)
    messages = []
    for container_name in container_names:
        nearest_position = find_nearest_container(ship_grid, origin)

        if nearest_position == (-1, -1):
            messages.append(f"Error: No containers found for unloading.")
            break

        row, col = nearest_position
        container = ship_grid[row][col].container

        if container.name != container_name:
            messages.append(f"Error: Nearest container does not match name '{container_name}'.")
            continue

        # Remove the container from the grid
        ship_grid[row][col] = Slot(container=None, hasContainer=False, available=True)
        messages.append(f"Container '{container_name}' unloaded from [{row + 1}, {col + 1}].")
    return messages
