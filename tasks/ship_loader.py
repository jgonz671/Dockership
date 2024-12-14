from tasks.ship_balancer import Container, Slot, manhattan_distance
import copy

def find_next_available_position(ship_grid):
    """
    Finds next available position column by column from left to right, 
    ensuring containers are placed on bottom-most available position.
    """
    cols = len(ship_grid[0])
    rows = len(ship_grid)
    
    for col_idx in range(cols):
        # Start from bottom of column and work up
        for row_idx in range(rows):
            # Check if current position is available
            if ship_grid[row_idx][col_idx].available:
                # If it's bottom row, this position is valid
                if row_idx == 0:
                    return row_idx, col_idx
                # If there's a container below, this position is valid
                elif not ship_grid[row_idx - 1][col_idx].available:
                    return row_idx, col_idx
    return -1, -1

def can_unload_container(ship_grid, row, col):
    """Check if container can be unloaded (has support underneath and no container above)."""
    # Check if there's a container above
    if row < len(ship_grid) - 1 and ship_grid[row + 1][col].hasContainer:
        return False
    
    # Check if it's bottom row or has support underneath
    if row == 0 or ship_grid[row - 1][col].hasContainer:
        return True
    
    return False

def find_nearest_container(ship_grid, target_name=None, origin=(0, 0)):
    """
    Finds nearest unloadable container, searching column by column from left to right.
    Container must have support underneath and no container above.
    """
    min_distance = float("inf")
    nearest_position = (-1, -1)

    for col_idx in range(len(ship_grid[0])):
        for row_idx in range(len(ship_grid)):
            slot = ship_grid[row_idx][col_idx]
            
            if not slot.hasContainer:
                continue
                
            if target_name and slot.container.name != target_name:
                continue
                
            if not can_unload_container(ship_grid, row_idx, col_idx):
                continue

            distance = manhattan_distance(origin, (row_idx, col_idx))
            if distance < min_distance:
                min_distance = distance
                nearest_position = (row_idx, col_idx)

    return nearest_position

def calculate_move_cost(start_pos, end_pos):
    """Calculate cost of moving container (60 seconds per slot)."""
    return manhattan_distance(start_pos, end_pos) * 60

def load_containers(ship_grid, container_names):
    """Load containers efficiently, starting from leftmost columns."""
    messages = []
    total_cost = 0
    origin = (len(ship_grid) - 1, 0)  # Start from top-left

    for container_name in container_names:
        current_pos = origin
        target_pos = find_next_available_position(ship_grid)

        if target_pos == (-1, -1):
            messages.append(f"Error: No available slots for container '{container_name}'.")
            continue

        # Calculate move cost
        move_cost = calculate_move_cost(current_pos, target_pos)
        total_cost += move_cost

        # Create container with random weight between 10000-100000
        import random
        weight = random.randint(10000, 100000)
        
        # Place container
        row, col = target_pos
        ship_grid[row][col] = Slot(
            container=Container(name=container_name, weight=weight),
            hasContainer=True,
            available=False
        )
        
        messages.append(
            f"Container '{container_name}' loaded at [{row + 1}, {col + 1}] "
            f"with weight {weight}. Move cost: {move_cost} seconds"
        )

    messages.append(f"Total loading cost: {total_cost} seconds")
    return messages, total_cost

def unload_containers(ship_grid, container_names):
    """Unload containers efficiently to top-left origin."""
    messages = []
    total_cost = 0
    origin = (len(ship_grid) - 1, 0)  # Start from top-left

    for container_name in container_names:
        container_pos = find_nearest_container(ship_grid, container_name, origin)

        if container_pos == (-1, -1):
            messages.append(
                f"Error: Container '{container_name}' not found or cannot be unloaded "
                f"(might be blocked by container above or have no support underneath)."
            )
            continue

        # Calculate move cost
        move_cost = calculate_move_cost(container_pos, origin)
        total_cost += move_cost

        # Remove container
        row, col = container_pos
        container = ship_grid[row][col].container
        ship_grid[row][col] = Slot(container=None, hasContainer=False, available=True)
        
        messages.append(
            f"Container '{container_name}' unloaded from [{row + 1}, {col + 1}]. "
            f"Move cost: {move_cost} seconds"
        )

    messages.append(f"Total unloading cost: {total_cost} seconds")
    return messages, total_cost