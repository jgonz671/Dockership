from tasks.ship_balancer import Container, Slot, manhattan_distance
from utils.log_manager import LogFileManager  # Import LogFileManager
import copy
log_manager = LogFileManager(db)

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

def find_blocking_containers(ship_grid, target_row, target_col):
    """Find containers that are stacked above the target container."""
    blocking = []
    for row in range(target_row + 1, len(ship_grid)):
        if ship_grid[row][target_col].hasContainer:
            blocking.append((row, target_col))
        else:
            break
    return blocking

def find_nearest_empty_column(ship_grid, col_to_avoid, containers_to_unload):
    """Find nearest column that can safely store temporary containers."""
    center_col = len(ship_grid[0]) // 2
    
    # Check columns alternating outward from the center
    for offset in range(len(ship_grid[0])):
        for direction in [-1, 1]:
            check_col = center_col + (offset * direction)
            if not (0 <= check_col < len(ship_grid[0])):
                continue
                
            if check_col == col_to_avoid:
                continue
                
            # Check if this column contains any containers to be unloaded
            column_safe = True
            for row in range(len(ship_grid)):
                if (ship_grid[row][check_col].hasContainer and 
                    ship_grid[row][check_col].container.name in containers_to_unload):
                    column_safe = False
                    break
                    
            if column_safe:
                # Find the first available position in this column
                for row in range(len(ship_grid)):
                    if not ship_grid[row][check_col].hasContainer:
                        return row, check_col
                        
    return -1, -1

def calculate_move_cost(start_pos, end_pos, is_first_move=False):
    """
    Calculate cost of moving container (60 seconds per slot).
    Adds 60 seconds for crane deployment on first move.
    """
    base_cost = manhattan_distance(start_pos, end_pos) * 60
    return base_cost + (60 if is_first_move else 0)

def move_container(ship_grid, from_pos, to_pos, messages, is_first_move=False):
    """Move a container from one position to another."""
    from_row, from_col = from_pos
    to_row, to_col = to_pos
    
    # Calculate move cost (add 60 seconds for crane deployment if first move)
    move_cost = calculate_move_cost(from_pos, to_pos, is_first_move)
    
    # Move the container
    container = ship_grid[from_row][from_col].container
    ship_grid[to_row][to_col] = Slot(container=container, hasContainer=True, available=False)
    ship_grid[from_row][from_col] = Slot(container=None, hasContainer=False, available=True)
    
    messages.append(
        f"Moved container '{container.name}' from [{from_row + 1}, {from_col + 1}] "
        f"to [{to_row + 1}, {to_col + 1}]. Move cost: {move_cost} seconds"
    )
    
    return move_cost

def load_containers(ship_grid, container_names):
    """Load containers efficiently, starting from leftmost columns."""
    messages = []
    total_cost = 0
    origin = (len(ship_grid) - 1, 0)  # Start from top-left
    first_move = True

    for container_name in container_names:
        current_pos = origin
        target_pos = find_next_available_position(ship_grid)

        if target_pos == (-1, -1):
            messages.append(f"Error: No available slots for container '{container_name}'.")
            continue

        # Calculate and add move cost
        move_cost = calculate_move_cost(current_pos, target_pos, first_move)
        total_cost += move_cost
        first_move = False

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
    """
    Unload containers efficiently, handling blocking containers.
    Containers can be unloaded in any order by moving blocking containers temporarily.
    """
    messages = []
    total_cost = 0
    origin = (len(ship_grid) - 1, 0)  # Top-left position
    container_names = set(container_names)  # Convert to set for faster lookup
    first_move = True
    
    # Create a queue of containers to unload with their positions
    containers_to_unload = []
    for row in range(len(ship_grid)):
        for col in range(len(ship_grid[0])):
            if (ship_grid[row][col].hasContainer and 
                ship_grid[row][col].container.name in container_names):
                containers_to_unload.append((row, col))
    
    # Sort by column first, then by row (bottom to top)
    containers_to_unload.sort(key=lambda x: (x[1], x[0]))
    
    for target_row, target_col in containers_to_unload:
        if not ship_grid[target_row][target_col].hasContainer:
            continue  # Container might have been moved already
            
        # Find blocking containers
        blocking = find_blocking_containers(ship_grid, target_row, target_col)
        
        # Move blocking containers to nearest empty column
        temp_moves = []  # Store temporary moves to restore later if needed
        for block_row, block_col in blocking:
            temp_row, temp_col = find_nearest_empty_column(
                ship_grid, target_col, container_names
            )
            
            if temp_row == -1:
                messages.append(
                    f"Error: No available temporary position for blocking container "
                    f"at [{block_row + 1}, {block_col + 1}]"
                )
                continue
                
            # Move blocking container
            cost = move_container(
                ship_grid, 
                (block_row, block_col), 
                (temp_row, temp_col), 
                messages, 
                first_move
            )
            total_cost += cost
            first_move = False
            temp_moves.append((temp_row, temp_col))
        
        # Now unload the target container
        cost = move_container(
            ship_grid,
            (target_row, target_col),
            origin,
            messages,
            first_move
        )
        total_cost += cost
        first_move = False
        
        # Remove container from grid
        ship_grid[origin[0]][origin[1]] = Slot(
            container=None, hasContainer=False, available=True
        )
        messages.append(
            f"Container '{ship_grid[target_row][target_col].container.name}' "
            f"unloaded from [{target_row + 1}, {target_col + 1}]"
        )
    
    messages.append(f"Total unloading cost: {total_cost} seconds")
    return messages, total_cost