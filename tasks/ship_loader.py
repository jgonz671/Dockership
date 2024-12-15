from copy import deepcopy
import random
import os
from tasks.ship_balancer import Container, Slot, manhattan_distance


def find_next_available_position(ship_grid):
    """Find next available bottom-most position."""
    cols = len(ship_grid[0])
    rows = len(ship_grid)

    for col_idx in range(cols):
        for row_idx in range(rows):
            if ship_grid[row_idx][col_idx].available:
                if row_idx == 0 or not ship_grid[row_idx - 1][col_idx].available:
                    return row_idx, col_idx
    return -1, -1

def find_blocking_containers(ship_grid, target_row, target_col):
    """Find containers stacked above target in top-to-bottom order."""
    blocking = []
    max_row = len(ship_grid)
    
    # Scan top-down starting from highest possible position
    for row in range(max_row - 1, target_row, -1):
        if ship_grid[row][target_col].hasContainer:
            blocking.append((row, target_col))
            
    return blocking  # Already in top-to-bottom order

def find_lowest_available_position(ship_grid, col):
    """Find lowest available position in column."""
    for row in range(len(ship_grid)):
        if ship_grid[row][col].available:
            if row == 0 or not ship_grid[row-1][col].available:
                return row
    return -1


def find_least_occupied_column(ship_grid, current_col, containers_to_unload):
    """Find column with fewest containers not in unload list."""
    min_containers = float('inf')
    best_col = -1
    
    for col in range(len(ship_grid[0])):
        if col == current_col:
            continue
            
        container_count = sum(
            1 for row in range(len(ship_grid)) 
            if ship_grid[row][col].hasContainer 
            and ship_grid[row][col].container.name not in containers_to_unload
        )
        
        if container_count < min_containers:
            min_containers = container_count
            best_col = col
            
    return best_col

def calculate_move_cost(start_pos, end_pos, is_first_move=False):
    """Calculate movement cost including first move penalty."""
    base_cost = manhattan_distance(start_pos, end_pos) * 60
    return base_cost + (60 if is_first_move else 0)

def move_container(ship_grid, from_pos, to_pos, messages, is_first_move=False):
    """Move container and update grid."""
    from_row, from_col = from_pos
    to_row, to_col = to_pos

    move_cost = calculate_move_cost(from_pos, to_pos, is_first_move)
    container = ship_grid[from_row][from_col].container
    
    ship_grid[to_row][to_col] = Slot(container=container, hasContainer=True, available=False)
    ship_grid[from_row][from_col] = Slot(container=None, hasContainer=False, available=True)

    messages.append(
        f"Moved container '{container.name}' from [{from_row + 1}, {from_col + 1}] "
        f"to [{to_row + 1}, {to_col + 1}]. Move cost: {move_cost} seconds"
    )

    return move_cost

def calculate_grid_capacity(ship_grid):
    """Calculate current capacity percentage."""
    total_slots = len(ship_grid) * len(ship_grid[0])
    occupied_slots = sum(1 for row in ship_grid for slot in row if slot.hasContainer)
    return (occupied_slots / total_slots) * 100


def find_nearest_available_column(ship_grid, current_col):
    """Find nearest available column, falling back to least occupied if needed."""
    cols = len(ship_grid[0])
    rows = len(ship_grid)
    
    # First try to find columns with direct available space
    column_scores = []
    
    for col in range(cols):
        if col == current_col:
            continue
            
        distance = abs(col - current_col)
        occupied_count = sum(1 for row in range(rows) if ship_grid[row][col].hasContainer)
        has_space = any(ship_grid[row][col].available for row in range(rows))
        
        if has_space:
            # Score based on distance and occupancy (lower is better)
            score = (distance * 10) + occupied_count
            column_scores.append((score, col))
    
    if column_scores:
        return min(column_scores, key=lambda x: x[0])[1]
        
    # If no columns with direct space, fall back to least occupied
    fallback_col = find_least_occupied_column(ship_grid, current_col, set())
    if fallback_col != -1:
        # Make space in this column by shifting containers up
        for row in range(rows-1, 0, -1):
            if ship_grid[row][fallback_col].hasContainer:
                # Move container up one position if possible
                if ship_grid[row-1][fallback_col].available:
                    container = ship_grid[row][fallback_col].container
                    ship_grid[row-1][fallback_col] = Slot(container=container, hasContainer=True, available=False)
                    ship_grid[row][fallback_col] = Slot(container=None, hasContainer=False, available=True)
        
        return fallback_col
      
    return -1

def move_blocking_container_low_capacity(ship_grid, block_row, block_col, container_names, messages, first_move):
    """Handle blocking container movement for low capacity."""
    target_col = find_nearest_available_column(ship_grid, block_col)
    
    if target_col == -1:
        return -1, None
    
    target_row = find_lowest_available_position(ship_grid, target_col)
    
    if target_row == -1:
        return -1, None
        
    cost = move_container(ship_grid, (block_row, block_col), (target_row, target_col), messages, first_move)
    return cost, (target_row, target_col)

def load_containers(ship_grid, container_names):
    """Load containers from origin."""
    messages = []
    total_cost = 0
    origin = (len(ship_grid) - 1, 0)
    first_move = True

    for container_name in container_names:
        target_pos = find_next_available_position(ship_grid)
        if target_pos == (-1, -1):
            messages.append(f"Error: No available positions for container '{container_name}'")
            continue

        move_cost = calculate_move_cost(origin, target_pos, first_move)
        total_cost += move_cost
        first_move = False

        weight = random.randint(10000, 100000)
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
    return ship_grid, messages, total_cost

def handle_origin_container(ship_grid, origin, container_names, current_capacity, messages, first_move):
    """Handle container at origin position based on grid capacity."""
    total_cost = 0
    buffer = []
    temp_position = None
    
    if not ship_grid[origin[0]][origin[1]].hasContainer:
        return total_cost, buffer, first_move, True, None
        
    origin_container = ship_grid[origin[0]][origin[1]].container
    if origin_container.name in container_names:
        return total_cost, buffer, first_move, True, None

    # Handle based on capacity
    if current_capacity > 50.0:
        # Use buffer for high capacity
        buffer.append((origin_container, origin[1], None))
        cost = calculate_move_cost(origin, (-1, len(buffer) - 1), first_move)
        messages.append(
            f"Moved container '{origin_container.name}' from origin to buffer. Move cost: {cost} seconds."
        )
        ship_grid[origin[0]][origin[1]] = Slot(container=None, hasContainer=False, available=True)
    else:
        # Use nearest available column for low capacity - leave container there
        target_col = find_nearest_available_column(ship_grid, origin[1])
        if target_col != -1:
            target_row = find_lowest_available_position(ship_grid, target_col)
            if target_row != -1:
                temp_position = (target_row, target_col)
                # Move container to new position permanently
                ship_grid[target_row][target_col] = Slot(container=origin_container, hasContainer=True, available=False)
                ship_grid[origin[0]][origin[1]] = Slot(container=None, hasContainer=False, available=True)
                cost = calculate_move_cost(origin, temp_position, first_move)
                messages.append(
                    f"Moved container '{origin_container.name}' from [{origin[0] + 1}, {origin[1] + 1}] to [{target_row + 1}, {target_col + 1}]. Move cost: {cost} seconds."
                )
                # Don't add to buffer since we're not restoring it
            else:
                messages.append(f"Error: No available position for origin container '{origin_container.name}'")
                return total_cost, buffer, first_move, False, None
        else:
            messages.append(f"Error: No available column for origin container '{origin_container.name}'")
            return total_cost, buffer, first_move, False, None
            
    total_cost += cost
    first_move = False
    
    return total_cost, buffer, first_move, True, temp_position

def unload_containers(ship_grid, container_names, buffer_capacity=5):
    """Unload containers efficiently, handling duplicates by selecting optimal positions."""
    messages = []
    total_cost = 0
    origin = (len(ship_grid) - 1, 0)
    container_names = set(container_names)
    first_move = True
    buffer = []
    unloaded_containers = set()

    current_capacity = calculate_grid_capacity(ship_grid)

    # Handle origin container first
    origin_cost, origin_buffer, first_move, success, temp_position = handle_origin_container(
        ship_grid, origin, container_names, current_capacity, messages, first_move
    )
    if not success:
        return ship_grid, messages, total_cost
    total_cost += origin_cost
    buffer.extend(origin_buffer)

    # Find all container positions including duplicates
    container_positions = find_container_positions(ship_grid, container_names)
    
    # Get optimal positions for containers with duplicates
    optimal_positions = get_optimal_container_positions(ship_grid, container_positions, origin)
    
    # Sort containers by position (top to bottom, left to right)
    containers_to_unload = [(name, pos) for name, pos in optimal_positions.items()]
    containers_to_unload.sort(key=lambda x: (-x[1][0], x[1][1]))

    # Process containers
    for container_name, current_pos in containers_to_unload:
        if container_name in unloaded_containers:
            continue

        # Handle blocking containers
        blocking = find_blocking_containers(ship_grid, current_pos[0], current_pos[1])
        for block_row, block_col in blocking:
            blocking_container = ship_grid[block_row][block_col].container
            if blocking_container.name in container_names:
                continue

            if current_capacity > 50.0 and len(buffer) < buffer_capacity:
                # Move to buffer
                buffer.append((blocking_container, block_col, None))
                cost = calculate_move_cost((block_row, block_col), (-1, len(buffer) - 1), first_move)
                messages.append(
                    f"Moved blocking container '{blocking_container.name}' to buffer. Move cost: {cost} seconds."
                )
                ship_grid[block_row][block_col] = Slot(container=None, hasContainer=False, available=True)
            else:
                # Move to nearest available position
                cost, new_pos = move_blocking_container_low_capacity(
                    ship_grid, block_row, block_col, container_names, messages, first_move
                )
                if cost == -1:
                    messages.append(f"Error: No available position for blocking container '{blocking_container.name}'.")
                    return ship_grid, messages, total_cost
            
            total_cost += cost
            first_move = False

        # Unload target container
        container = ship_grid[current_pos[0]][current_pos[1]].container
        cost = move_container(ship_grid, current_pos, origin, messages, first_move)
        total_cost += cost
        first_move = False
        
        unloaded_containers.add(container_name)
        ship_grid[origin[0]][origin[1]] = Slot(container=None, hasContainer=False, available=True)
        messages.append(f"Container '{container_name}' successfully unloaded from [{current_pos[0] + 1}, {current_pos[1] + 1}].")

    # Restore buffer containers for high capacity case
    if current_capacity > 50.0:
        while buffer:
            container, original_col, _ = buffer.pop(0)
            if container.name in container_names:
                continue

            target_row = find_lowest_available_position(ship_grid, original_col)
            if target_row == -1:
                target_pos = find_next_available_position(ship_grid)
                if target_pos == (-1, -1):
                    messages.append(f"Error: No available position to restore container '{container.name}' from buffer.")
                    continue
                row, col = target_pos
            else:
                row, col = target_row, original_col

            ship_grid[row][col] = Slot(container=container, hasContainer=True, available=False)
            messages.append(f"Restored container '{container.name}' from buffer to [{row + 1}, {col + 1}].")

    messages.append(f"Total unloading cost: {total_cost} seconds.")
    return ship_grid, messages, total_cost


def convert_grid_to_manuscript(ship_grid):
    """Convert grid to manuscript format."""
    manuscript_lines = []
    for row in ship_grid:
        for slot in row:
            if slot.hasContainer:
                manuscript_lines.append(f"{slot.container.name},{slot.container.weight}")
    return "\n".join(manuscript_lines)

def append_outbound_to_filename(filename):
    """Append OUTBOUND to filename."""
    name, ext = os.path.splitext(filename)
    return f"{name}_OUTBOUND{ext}"

def find_container_positions(ship_grid, container_names):
    """Find all positions of containers, including duplicates."""
    container_positions = {}
    
    for row in range(len(ship_grid)-1, -1, -1):
        for col in range(len(ship_grid[0])):
            if ship_grid[row][col].hasContainer:
                name = ship_grid[row][col].container.name
                if name in container_names:
                    if name not in container_positions:
                        container_positions[name] = []
                    container_positions[name].append((row, col))
                    
    return container_positions

def estimate_unload_cost(ship_grid, container_pos, origin):
    """Estimate total cost to unload container including moving blocking containers."""
    row, col = container_pos
    total_cost = calculate_move_cost(container_pos, origin, True)
    
    # Add cost of moving blocking containers
    blocking = find_blocking_containers(ship_grid, row, col)
    for block_pos in blocking:
        # Estimate cost to nearest available column
        target_col = find_nearest_available_column(ship_grid, block_pos[1])
        if target_col != -1:
            target_row = find_lowest_available_position(ship_grid, target_col)
            if target_row != -1:
                total_cost += calculate_move_cost(block_pos, (target_row, target_col), False)
                
    return total_cost

def get_optimal_container_positions(ship_grid, container_positions, origin):
    """For containers with duplicates, select position with lowest unload cost."""
    optimal_positions = {}
    
    for name, positions in container_positions.items():
        if len(positions) > 1:
            # Find position with lowest total unload cost
            costs = [(pos, estimate_unload_cost(ship_grid, pos, origin)) for pos in positions]
            optimal_pos = min(costs, key=lambda x: x[1])[0]
            optimal_positions[name] = optimal_pos
        else:
            optimal_positions[name] = positions[0]
            
    return optimal_positions


# def unload_containers(ship_grid, container_names, buffer_capacity=5): 
#     messages = [] 
#     total_cost = 0 
#     origin = (len(ship_grid) - 1, 0) # [8,1] position 
#     container_names = set(container_names) 
#     first_move = True 
#     buffer = [] 
#     container_positions = {} 
#     unloaded_containers = set()

#     current_capacity = calculate_grid_capacity(ship_grid)
#     use_buffer = current_capacity > 50.0

#     # Find and sort containers to unload
#     containers_to_unload = []
#     for row in range(len(ship_grid)-1, -1, -1):
#         for col in range(len(ship_grid[0])):
#             if (ship_grid[row][col].hasContainer and 
#                 ship_grid[row][col].container.name in container_names):
#                 containers_to_unload.append((row, col))
#                 container_positions[ship_grid[row][col].container.name] = (row, col)

#     containers_to_unload.sort(key=lambda x: (-x[0], x[1]))

#     # Handle container at origin if present
#     origin_empty = True
#     if ship_grid[origin[0]][origin[1]].hasContainer:
#         origin_container = ship_grid[origin[0]][origin[1]].container
#         if origin_container.name not in container_names:
#             buffer.append((origin_container, origin[1]))
#             cost = calculate_move_cost(origin, (-1, len(buffer) - 1), first_move)
#             messages.append(
#                 f"Moved container '{origin_container.name}' from origin to buffer. Move cost: {cost} seconds."
#             )
#             ship_grid[origin[0]][origin[1]] = Slot(container=None, hasContainer=False, available=True)
#             total_cost += cost
#             first_move = False
#             origin_empty = True

#     for target_row, target_col in containers_to_unload:
#         target_container = ship_grid[target_row][target_col].container
#         if not target_container or target_container.name in unloaded_containers:
#             continue

#         current_pos = container_positions.get(target_container.name, (target_row, target_col))

#         # Handle blocking containers
#         blocking = find_blocking_containers(ship_grid, current_pos[0], current_pos[1])
#         for block_row, block_col in blocking:
#             blocking_container = ship_grid[block_row][block_col].container
#             if blocking_container.name in container_names:
#                 continue

#             if use_buffer and len(buffer) < buffer_capacity:
#                 buffer.append((blocking_container, block_col))
#                 cost = calculate_move_cost((block_row, block_col), (-1, len(buffer) - 1), first_move)
#                 messages.append(
#                     f"Moved blocking container '{blocking_container.name}' to buffer. Move cost: {cost} seconds."
#                 )
#                 ship_grid[block_row][block_col] = Slot(container=None, hasContainer=False, available=True)
#             else:
#                 cost, new_pos = move_blocking_container_low_capacity(
#                     ship_grid, block_row, block_col, container_names, messages, first_move
#                 )
#                 if cost == -1:
#                     messages.append(f"Error: No available position for blocking container '{blocking_container.name}'.")
#                     return ship_grid, messages, total_cost
#                 container_positions[blocking_container.name] = new_pos
            
#             total_cost += cost
#             first_move = False

#         # Unload target container
#         current_pos = container_positions[target_container.name]
#         cost = move_container(ship_grid, current_pos, origin, messages, first_move)
#         total_cost += cost
#         first_move = False
        
#         # Mark as unloaded
#         unloaded_containers.add(target_container.name)
#         ship_grid[origin[0]][origin[1]] = Slot(container=None, hasContainer=False, available=True)
#         messages.append(f"Container '{target_container.name}' successfully unloaded from [{current_pos[0] + 1}, {current_pos[1] + 1}].")
        
#         del container_positions[target_container.name]

#         # Restore origin container immediately if it was the only one to unload
#         if len(containers_to_unload) == 1 and buffer and buffer[0][0].name not in container_names:
#             origin_container, _ = buffer.pop(0)
#             ship_grid[origin[0]][origin[1]] = Slot(container=origin_container, hasContainer=True, available=False)
#             messages.append(f"Restored container '{origin_container.name}' to origin position [8, 1].")

#     # Restore remaining buffer containers
#     while buffer:
#         container, original_col = buffer.pop(0)
#         if container.name in container_names:
#             continue

#         # Special handling for origin container
#         if original_col == origin[1] and origin_empty:
#             ship_grid[origin[0]][origin[1]] = Slot(container=container, hasContainer=True, available=False)
#             messages.append(f"Restored container '{container.name}' to origin position [8, 1].")
#             continue
            
#         target_row = find_lowest_available_position(ship_grid, original_col)
#         if target_row == -1:
#             target_pos = find_next_available_position(ship_grid)
#             if target_pos == (-1, -1):
#                 messages.append(f"Error: No available position to restore container '{container.name}' from buffer.")
#                 continue
#             row, col = target_pos
#         else:
#             row, col = target_row, original_col

#         ship_grid[row][col] = Slot(container=container, hasContainer=True, available=False)
#         messages.append(f"Restored container '{container.name}' from buffer to [{row + 1}, {col + 1}].")

#     messages.append(f"Total unloading cost: {total_cost} seconds.")
#     return ship_grid, messages, total_cost

