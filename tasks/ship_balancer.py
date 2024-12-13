import copy
import re
import numpy as np
import time
import plotly.graph_objects as go

from collections.abc import Iterable


class Container:
    def __init__(self, name, weight):
        self.name = name
        self.name_adj = re.findall(r'^.*\d{4}', name)
        self.name_check = False
        self.weight = weight


class Slot:
    def __init__(self, container: Container, hasContainer, available):
        self.container = container  # Container object or None
        self.has_container = hasContainer  # Boolean: True if container is present
        self.available = available  # Boolean: True if slot is available


# Create a ship grid with size
def create_ship_grid(rows, columns):
    ship_grid = []

    for i in range(rows):
        container_row = []
        for _ in range(columns):
            container_row.append(Slot(None, False, False))
        ship_grid.append(container_row)

    return ship_grid


# Function to parse the manuscript
def parse_manifest(file_lines):
    """
    Parses the manuscript file to create a structured grid.
    Each entry in the manuscript is assumed to be in the format: [row,col], {weight}, name.
    """
    grid = []
    max_row, max_col = 0, 0

    for line in file_lines:
        parts = line.strip().split(", ")
        if len(parts) != 3:
            continue

        # Parse row and column
        row_col = parts[0].strip("[]").split(",")
        row, col = int(row_col[0]), int(row_col[1])

        # Parse weight and name
        weight = int(parts[1].strip("{}"))
        name = parts[2]

        max_row = max(max_row, row)
        max_col = max(max_col, col)

        grid.append((row, col, weight, name))

    # Create a grid of appropriate size
    ship_grid = [["Empty" for _ in range(max_col)] for _ in range(max_row)]
    for row, col, weight, name in grid:
        ship_grid[row - 1][col - 1] = {"name": name, "weight": weight}

    return ship_grid

# Function to visualize the grid


def visualize_ship_grid(ship_grid, title="Ship Grid"):
    """
    Visualizes the ship's grid layout using Plotly.
    """
    z = []
    hover_text = []
    annotations = []

    # Reverse rows for bottom-left origin
    for row_index, row in enumerate(reversed(ship_grid)):
        z_row = []
        hover_row = []
        for col_index, slot in enumerate(row):
            position = f"({len(ship_grid) - row_index}, {col_index + 1})"

            if isinstance(slot, dict):  # Occupied slot
                z_row.append(1)
                hover_row.append(
                    f"Position: {position}<br>Name: {slot['name']}<br>Weight: {slot['weight']}")
                annotations.append(
                    dict(
                        x=col_index + 1,
                        y=len(ship_grid) - row_index,
                        text=slot["name"],
                        showarrow=False,
                        font=dict(color="white", size=10),
                    )
                )
            elif slot == "Empty":  # Empty slot
                z_row.append(0)
                hover_row.append(f"Position: {position}<br>Empty Slot")
            else:  # Special cases like NAN
                z_row.append(-1)
                hover_row.append(f"Position: {position}<br>{slot}")
                annotations.append(
                    dict(
                        x=col_index + 1,
                        y=len(ship_grid) - row_index,
                        text=slot,
                        showarrow=False,
                        font=dict(color="black", size=10),
                    )
                )

        z.append(z_row)
        hover_text.append(hover_row)

    # Create heatmap
    fig = go.Figure(
        data=go.Heatmap(
            z=z,
            colorscale=[[0, "white"], [0.5, "gray"], [1, "blue"]],
            hoverinfo="text",
            text=hover_text,
            showscale=False,
        )
    )

    # Add annotations for labels
    fig.update_layout(
        annotations=annotations,
        title=title,
        xaxis=dict(
            title="Columns",
            showgrid=False,
            zeroline=False,
            tickmode="linear",
            tick0=1,
            dtick=1,
        ),
        yaxis=dict(
            title="Rows",
            showgrid=False,
            zeroline=False,
            tickmode="linear",
            tick0=1,
            dtick=1,
            scaleanchor="x",
        ),
    )

    return fig


# Update ship grid with manifest info, update list of containers accordingly
# Update the ship grid based on file data
def update_ship_grid(lines, ship_grid, containers):
    for line in lines:
        slot_data = line.split()
        loc = [int(val) - 1 for val in re.sub(r"[\[\]]",
                                              '', slot_data[0]).split(",")[:2]]
        weight = int(re.sub(r"[\{\}\,]", '', slot_data[1]))
        status = slot_data[2] if len(
            slot_data) < 3 else " ".join(slot_data[2:])
        x, y = loc

        if status == "NAN":
            ship_grid[x][y] = Slot(None, has_container=False, available=False)
        elif status == "UNUSED":
            ship_grid[x][y] = Slot(None, has_container=False, available=True)
        else:
            ship_grid[x][y] = Slot(
                Container(status, weight), has_container=True, available=False)
            if len(ship_grid[x][y].container.name_adj) > 0:
                ship_grid[x][y].container.name_check = True
            containers.append(loc)


# Given ship grid, outputs matrix representing grid
def print_grid(ship_grid):
    adj_ship_grid = []
    for row in ship_grid:
        adj_ship_grid.append(
            [1 if slot.has_container == True else 0 for slot in row])

    for x, row in enumerate(ship_grid):
        for y, container in enumerate(row):

            if (ship_grid[x][y].container is not None):
                adj_ship_grid[x][y] = ship_grid[x][y].container.name[0]
            else:
                if (ship_grid[x][y].available == False):
                    adj_ship_grid[x][y] = 'X'

    print(np.array(adj_ship_grid[::-1][:]))


def load(containers_and_locs, ship_grid):

    ship_grids, store_goals = [], []

    steps, unloading_zone = [], [len(ship_grid) - 1, 0]

    containers_and_locs = sorted(containers_and_locs, key=lambda x: x[1][0])

    for idx, (container, loc) in enumerate(containers_and_locs):
        ship_grid[unloading_zone[0]][unloading_zone[1]].container = container
        ship_grid[unloading_zone[0]][unloading_zone[1]].has_container = True
        ship_grid[unloading_zone[0]][unloading_zone[1]].available = False

        orig_ship_grid = copy.deepcopy(ship_grid)

        extra_steps, extra_grids = move_to(
            unloading_zone, loc, ship_grid, store_goals)

        if not extra_steps:
            # If no possible steps, container is being blocked
            ship_grid = orig_ship_grid
            containers = []
            for r, row in enumerate(ship_grid):
                for c, slot in enumerate(row):
                    if slot.has_container is True and [r, c] != unloading_zone:
                        containers.append([r, c])

            sorted_containers = sorted(
                containers, key=lambda x: x[0], reverse=True)
            new_loc = nearest_available(sorted_containers[0], ship_grid)
            extra_steps, extra_grids = move_to(
                sorted_containers[0], new_loc, ship_grid, store_goals)

            new_steps, new_grids = move_to(
                unloading_zone, loc, ship_grid, store_goals)

            extra_steps.append(new_steps)
            extra_grids.append(new_grids)

        steps.append(extra_steps)
        # steps[idx].insert(0, "[8, 0] to [7, 0]")
        ship_grids.append(extra_grids)

    r, c = np.array(ship_grid).shape
    ship_grids = reformat_grid_list(ship_grids, r, c)

    steps = reformat_step_list(steps, store_goals)

    return steps, ship_grids


def unload(containers_to_unload, ship_grid):

    # order containers by height, descending
    containers = sorted(containers_to_unload, key=lambda r: r[0], reverse=True)

    ship_grids, store_goals = [], []

    orig_ship_grid = copy.deepcopy(ship_grid)

    steps, unloading_zone = [], [len(ship_grid) - 1, 0]
    # move each container to unloading zone
    for container_loc in containers:
        extra_steps, extra_grids = move_to(
            container_loc, unloading_zone, ship_grid, store_goals)

        if not extra_steps:
            # If no possible steps, container is being blocked
            ship_grid = orig_ship_grid
            containers = []
            for r, row in enumerate(ship_grid):
                for c, slot in enumerate(row):
                    if slot.has_container is True and [r, c] != container_loc:
                        containers.append([r, c])

            sorted_containers = sorted(
                containers, key=lambda x: x[0], reverse=True)
            new_loc = nearest_available(sorted_containers[0], ship_grid)
            extra_steps, extra_grids = move_to(
                sorted_containers[0], new_loc, ship_grid, store_goals)

            new_steps, new_grids = move_to(
                container_loc, unloading_zone, ship_grid, store_goals)

            extra_steps.append(new_steps)
            extra_grids.append(new_grids)

        steps.append(extra_steps)
        ship_grids.append(extra_grids)

        # steps[-1].append(str(unloading_zone) + " to " + "[8, 0]")

        # Remove container from grid
        ship_grid[unloading_zone[0]][unloading_zone[1]].container = None
        ship_grid[unloading_zone[0]][unloading_zone[1]].has_container = False
        ship_grid[unloading_zone[0]][unloading_zone[1]].available = True

    r, c = np.array(ship_grid).shape
    ship_grids = reformat_grid_list(ship_grids, r, c)

    steps = reformat_step_list(steps, store_goals)

    return steps, ship_grids


# Returns move steps and status code (success or failure)
def balance(ship_grid, containers):
    """
    Balances the ship by moving containers between halves.

    Args:
        ship_grid (list[list[Slot]]): The grid representing the ship's layout.
        containers (list[tuple[int, int]]): List of container coordinates in the grid.

    Returns:
        tuple: Steps taken to balance, the updated ship grids after each step, and a boolean indicating success.
    """
    # Initialize variables
    steps = []  # Stores human-readable steps for each operation
    ship_grids = []  # Tracks ship grid states after each operation
    balanced = False  # Tracks if the ship is balanced

    # Ensure containers list is not empty
    if not containers:
        return steps, ship_grids, True

    # Main balancing loop
    while not balanced:
        # Calculate current balance
        left_balance, right_balance, balanced = calculate_balance(ship_grid)
        if balanced:
            break  # Exit loop if already balanced

        # Identify heavier side
        heavier_side = "left" if left_balance > right_balance else "right"
        target_side = "right" if heavier_side == "left" else "left"

        # Find containers on the heavier side
        halfway_line = len(ship_grid[0]) // 2
        if heavier_side == "left":
            containers_to_move = [
                (x, y) for x, y in containers if y < halfway_line and ship_grid[x][y].has_container
            ]
        else:
            containers_to_move = [
                (x, y) for x, y in containers if y >= halfway_line and ship_grid[x][y].has_container
            ]

        # No containers to move; balancing not possible
        if not containers_to_move:
            return steps, ship_grids, False

        # Attempt to move a container to the opposite side
        for x, y in containers_to_move:
            slot = ship_grid[x][y]
            if slot.container:
                # Determine target column on the opposite side
                target_col = (
                    len(ship_grid[0]) - y - 1) if heavier_side == "left" else (y - halfway_line)
                if target_col < 0 or target_col >= len(ship_grid[0]):
                    continue

                # Find an available slot on the target side
                if not ship_grid[x][target_col].has_container and ship_grid[x][target_col].available:
                    # Move container
                    ship_grid[x][target_col] = Slot(
                        slot.container, True, False)
                    ship_grid[x][y] = Slot(None, False, True)
                    steps.append(
                        f"Moved container {slot.container.name} from [{x+1},{y+1}] to [{x+1},{target_col+1}]")
                    ship_grids.append(copy.deepcopy(
                        ship_grid))  # Save grid state
                    break  # Move one container per iteration

        # Recalculate container positions after the move
        containers = [
            (x, y) for x, row in enumerate(ship_grid) for y, slot in enumerate(row) if slot.has_container
        ]

    return steps, ship_grids, balanced


def sift(ship_grid, containers, store_goals):
    steps, ship_grids = [], []

    # containers sorted by weights (ascending)
    container_weights = sorted([(container, ship_grid[container[0]][container[1]].container)
                               for container in containers], key=lambda container: container[1].weight, reverse=True)
    sorted_container_weights = [tup[0] for tup in container_weights]

    all_sift_slots = calculate_all_sift_slots(ship_grid)
    new_loc = None

    for idx, container in enumerate(sorted_container_weights):

        # check if container was moved already without updating
        if ship_grid[container[0]][container[1]].has_container is False:
            # find container
            for moves in store_goals:
                try:
                    if list(moves).index(str(container)) == 0:
                        # update container location
                        new_loc = moves[1]
                        sorted_container_weights[idx] = [
                            int(l) for l in new_loc.strip('][').split(', ')]
                        container = sorted_container_weights[idx]
                        break
                except ValueError:
                    pass

        next_move = all_sift_slots[0]
        del all_sift_slots[0]
        # while current slot is NaN, cycle through available slots
        while ship_grid[next_move[0]][next_move[1]].has_container is False and \
                ship_grid[next_move[0]][next_move[1]].available is False:

            del all_sift_slots[0]
            # get next available slot
            next_move = all_sift_slots[0]

        if next_move == container:
            # container is already in place
            continue

        # if there is a container, proceed to move it
        if ship_grid[next_move[0]][next_move[1]].has_container is True:
            nearest_avail = nearest_available(next_move, ship_grid)
            # move container to nearest available
            extra_steps, extra_grids = move_to(
                next_move, nearest_avail, ship_grid, store_goals)
            steps.append(extra_steps)
            ship_grids.append(extra_grids)

            sorted_container_weights[sorted_container_weights.index(
                next_move)] = nearest_avail
        # move container to original next move
        extra_steps, extra_grids = move_to(
            container, next_move, ship_grid, store_goals)
        steps.append(extra_steps)
        ship_grids.append(extra_grids)

        sorted_container_weights[idx] = next_move

    return steps, ship_grids


def calculate_all_sift_slots(ship_grid):
    halfway_line = len(ship_grid[0]) / 2

    all_slots = []

    for r in range(len(ship_grid)):
        p = -1
        curr_slot = [r, halfway_line - 1]
        for c in range(len(ship_grid[0])):
            slot = [r, int((curr_slot[1] + (c * pow(-1, p)))) % 12]
            p += 1
            all_slots.append(slot)
            curr_slot = slot

    return all_slots


def move_to(container_loc, goal_loc, ship_grid, store_goals):
    steps, ship_grids = [], []
    curr_container_loc = copy.deepcopy(container_loc)

    visited = []

    while (curr_container_loc != goal_loc):

        # print("cuur-goal:", curr_container_loc, goal_loc)

        curr_container = ship_grid[curr_container_loc[0]
                                   ][curr_container_loc[1]].container

        # if (curr_container is not None):
        visited.append((curr_container, curr_container_loc))

        # return valid neighbors
        valid_moves = return_valid_moves(curr_container_loc, ship_grid)

        if not valid_moves:
            if curr_container_loc[0] < len(ship_grid) - 1:
                if ship_grid[curr_container_loc[0] + 1][curr_container_loc[1]].has_container:
                    # print("No valid moves for current container {}... Moving container above".format(str(curr_container_loc)S))
                    extra_steps, extra_grids = move_container_above(
                        curr_container_loc, ship_grid, store_goals)
                    steps.append(extra_steps)
                    ship_grids.append(extra_grids)
                    valid_moves = return_valid_moves(
                        curr_container_loc, ship_grid)

        distances = []
        for neighbor in valid_moves:
            distances.append(
                (neighbor, manhattan_distance(neighbor, goal_loc)))

        distances = sorted(distances, key=lambda x: x[1])

        next_move = [-1, -1]
        # If there are two options of the same distance
        same_distances = [
            tup for tup in distances if tup[1] == distances[0][1]]
        if len(same_distances) > 1:
            num_moves = [(loc, abs(loc[1] - goal_loc[1]), d)
                         for loc, d in same_distances]
            if not num_moves:
                print("No moves possible!")
                return [], []
            possible_move, _, d = min(num_moves, key=lambda x: x[1])
            # cycle through possible moves until a new move is reached
            while (curr_container, possible_move) in visited:
                same_distances.remove((possible_move, d))
                num_moves = [(loc, abs(loc[1] - goal_loc[1]), d)
                             for loc, d in same_distances]
                if not num_moves:
                    print("No moves possible!")
                    return [], []
                possible_move, _, d = min(num_moves, key=lambda x: x[1])
            # If there is still an available new move
            if (len(same_distances) > 0):
                next_move = possible_move
        else:
            # no equivalent moves, choose best move
            for next_loc, distance in distances:
                if (curr_container, next_loc) not in visited:
                    next_move = next_loc
                    break

        steps.append(str(curr_container_loc) + " to " + str(next_move))

        # No valid moves
        if next_move == [-1, -1]:
            return_valid_moves(curr_container_loc, ship_grid)
            print("No valid moves!")
            break

        ship_grid[curr_container_loc[0]][curr_container_loc[1]], ship_grid[next_move[0]][next_move[1]] = \
            ship_grid[next_move[0]][next_move[1]
                                    ], ship_grid[curr_container_loc[0]][curr_container_loc[1]]

        curr_container_loc = copy.deepcopy(next_move)

    # print_grid(ship_grid)
    ship_grids.append(copy.deepcopy(ship_grid))

    store_goals.append((str(container_loc), str(goal_loc)))

    return steps, ship_grids


def compute_cost(container_loc, goal_loc, ship_grid):
    steps = []
    curr_container_loc = copy.deepcopy(container_loc)

    visited = []

    while (curr_container_loc != goal_loc):

        curr_container = ship_grid[curr_container_loc[0]
                                   ][curr_container_loc[1]].container

        # if (curr_container is not None):
        visited.append((curr_container, curr_container_loc))

        # return valid neighbors
        valid_moves = return_valid_moves(curr_container_loc, ship_grid)

        if not valid_moves:
            if curr_container_loc[0] < len(ship_grid) - 1:
                if ship_grid[curr_container_loc[0] + 1][curr_container_loc[1]].has_container:
                    print(
                        "No valid moves for current container... Moving container above")
                    extra_steps,  _ = move_container_above(
                        curr_container_loc, ship_grid, [])
                    steps.append(extra_steps)

        distances = []
        for neighbor in valid_moves:
            distances.append(
                (neighbor, manhattan_distance(neighbor, goal_loc)))

        distances = sorted(distances, key=lambda x: x[1])

        next_move = [-1, -1]
        for next_loc, distance in distances:
            if (curr_container, next_loc) not in visited:
                next_move = next_loc
                break

        steps.append(str(curr_container_loc) + " to " + str(next_move))

        # No valid moves
        if next_move == [-1, -1]:
            break

        ship_grid[curr_container_loc[0]][curr_container_loc[1]], ship_grid[next_move[0]][next_move[1]] = \
            ship_grid[next_move[0]][next_move[1]
                                    ], ship_grid[curr_container_loc[0]][curr_container_loc[1]]

        curr_container_loc = copy.deepcopy(next_move)

    # print_grid(ship_grid)

    return steps


def move_container_above(container_loc, ship_grid, store_goals):
    steps, ship_grids = [], []
    container_above = [container_loc[0] + 1, container_loc[1]]

    if (container_above[0] < len(ship_grid) - 1):
        if (ship_grid[container_above[0] + 1][container_above[1]].has_container):
            extra_steps, extra_grids = move_container_above(
                container_above, ship_grid, store_goals)
            steps.append(extra_steps)
            ship_grids.append(extra_grids)

    nearest_avail = nearest_available(container_above, ship_grid)

    extra_steps, extra_grids = move_to(
        container_above, nearest_avail, ship_grid, store_goals)
    steps.append(extra_steps)
    ship_grids.append(extra_grids)

    return steps, ship_grids


# Finds nearest available slot to the side of container_loc column
def nearest_available(container_loc, ship_grid):

    line_at_container = container_loc[1]

    open_slots = []

    for r, row in enumerate(ship_grid):
        for c, slot in enumerate(row):
            # Check if slot is available and is not hovering in the air
            if slot.available is True:
                # If slot is on the ground or If slot is not hovering in the air
                if (r == 0 or ship_grid[r - 1][c].available is False) and c != line_at_container:
                    open_slots.append([r, c])

    distances = []
    for slot in open_slots:
        distances.append(
            (slot, len(compute_cost(container_loc, slot, copy.deepcopy(ship_grid)))))

    distances = sorted(distances, key=lambda x: x[1])

    return distances[0][0]


# returns list of valid moves for container loc
def return_valid_moves(container_loc, ship_grid):

    if container_loc[0] < len(ship_grid) - 1:
        if ship_grid[container_loc[0] + 1][container_loc[1]].has_container is True:
            return []

    neighbors = []
    # We only consider four neighbors
    neighbors.append([container_loc[0] - 1, container_loc[1]])
    neighbors.append([container_loc[0] + 1, container_loc[1]])
    neighbors.append([container_loc[0], container_loc[1] - 1])
    neighbors.append([container_loc[0], container_loc[1] + 1])

    # only neighbors inside the grid, (x, y) >= 0
    neighbors = [neighbor for neighbor in neighbors if neighbor[0] >= 0 and neighbor[0] <= 7 and
                 neighbor[1] >= 0 and neighbor[1] <= 11]

    valid_moves = []

    for neighbor in neighbors:
        if ship_grid[neighbor[0]][neighbor[1]].available is True and \
                ship_grid[neighbor[0]][neighbor[1]]:
            valid_moves.append(neighbor)

    return valid_moves


# returns the manhattan distance heuristic evaluation
def manhattan_distance(container_loc, goal_loc):
    return abs(container_loc[0] - goal_loc[0]) + abs(container_loc[1] - goal_loc[1])


def nearest_available_balance(left_balance, right_balance, ship_grid):

    halfway_line = int(len(ship_grid[0]) / 2)

    # Check side with lower weight for available slots
    if left_balance > right_balance:
        ship_grid_adjusted = [row[halfway_line:] for row in ship_grid]
    else:
        ship_grid_adjusted = [row[:halfway_line] for row in ship_grid]

    for x, row in enumerate(ship_grid_adjusted):
        for y, slot in enumerate(row):
            # Check if slot is available and is not hovering in the air
            if slot.available is True:
                # If slot is on the ground
                if y == 0:
                    # If dealing with right half
                    if (left_balance > right_balance):
                        return x, y + 6
                    else:
                        return x, y
                # If slot is not hovering in the air
                if ship_grid[x][y - 1].available is False:
                    # If dealing with right half
                    if (left_balance > right_balance):
                        return x, y + 6
                    else:
                        return x, y

    return -1, -1


# Returns closeness to perfect balance (1.0)
def close_to_balance(ship_grid, container_loc, left_balance, right_balance):

    container_weight = ship_grid[container_loc[0]
                                 ][container_loc[1]].container.weight

    if left_balance > right_balance:
        closeness = (left_balance - container_weight) / \
            (right_balance + container_weight)
    else:
        closeness = (right_balance - container_weight) / \
            (left_balance + container_weight)

    return abs(1.0 - closeness)


# Calculate ship balance
def calculate_balance(ship_grid):
    left_balance, right_balance = 0, 0
    halfway_line = len(ship_grid[0]) // 2

    for row in ship_grid:
        for col, slot in enumerate(row):
            if not slot.container:
                continue
            if col < halfway_line:
                left_balance += slot.container.weight
            else:
                right_balance += slot.container.weight

    balanced = 0.9 <= left_balance / \
        right_balance <= 1.1 if right_balance > 0 else False
    return left_balance, right_balance, balanced


def update_manifest(ship_grid):
    manifest_info = []
    manifest_row = ''
    for r, row in enumerate(ship_grid):
        for c, slot in enumerate(row):
            manifest_row = "[" + \
                "{0:0=2d}".format(r + 1) + ',' + \
                "{0:0=2d}".format(c + 1) + "], "
            weight = 0 if slot.has_container is False else slot.container.weight
            manifest_row += "{" + "{0:0=5d}".format(weight) + "}, "
            name = 'NAN' if slot.has_container is False and slot.available is False else \
                'UNUSED' if slot.has_container is False and slot.available is True else \
                slot.container.name
            manifest_row += name
            manifest_info.append(manifest_row)
    return manifest_info


def flatten(l):
    for el in l:
        if isinstance(el, Iterable) and not isinstance(el, (str, bytes)):
            yield from flatten(el)
        else:
            yield el


def divide_list(l, n):

    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]


def reshape_to_grids(l, r, c):
    grids = []
    for el in l:
        grids.append(np.array(el).reshape(r, c).tolist())

    return grids


def reformat_grid_list(ship_grids, r, c):
    formatted = list(flatten(copy.deepcopy(ship_grids)))
    formatted = list(divide_list(formatted, r * c))
    formatted = reshape_to_grids(formatted, r, c)

    return formatted


def reformat_step_list(steps, store_goals):
    str_steps = str(list(flatten(steps)))
    store = []
    for start, goal in store_goals:
        s_idx = str_steps.find(start)
        e_idx = str_steps.find(goal)
        step = str_steps[s_idx-1:e_idx+(len(goal)+1)]
        str_steps = str_steps[e_idx+(len(goal)+1):]
        store.append(step)

    step_list = []
    for move_list in store:
        move_list = move_list.replace('\'', '')
        step_list.append([s + ']' for s in move_list.split("], ")])

    for move_list in step_list:
        move_list[-1] = move_list[-1][:len(move_list[-1])-1]

    # remove empty move_lists:
    for idx, move_list in enumerate(step_list):
        if len(move_list) == 1 and len(move_list[0]) <= 1:
            step_list.remove(move_list)

    return step_list


if __name__ == "__main__":

    ship_grid = create_ship_grid(8, 12)

    containers = []

    # Place containers manually
    if (input("Enter input manually?: ").lower() == 'y'):
        for n in range(int(input("Number of Containers: "))):

            container_loc = [int(l) for l in input(
                "Enter location, space-separated: ").split()]
            container_name = input("Enter name of container: ")
            container_weight = input("Enter weight of container: ")
            print("Entering container into system...\n")

            ship_grid[container_loc[0]][container_loc[1]].container = Container(
                container_name, container_weight)
            ship_grid[container_loc[0]][container_loc[1]].has_container = True

            containers.append(container_loc)
    else:
        file_loc = input("Enter file directory, or none for default: ")
        file = open("samples/CUNARD_BLUE.txt",
                    "r") if file_loc == "" else open(file_loc, "r")

        update_ship_grid(file, ship_grid, containers)

    if input("Proceed with balancing? (y/n): ") == "y":
        left_balance, right_balance, balanced = calculate_balance(ship_grid)
        total_weight = left_balance + right_balance

        print_grid(ship_grid)

        print("Total Weight:", total_weight)
        print("Left Balance:", left_balance)
        print("Right Balance:", right_balance)

        if balanced:
            print("Balanced!")
        else:
            print("Not Balanced!")
            steps, ship_grids, status = balance(ship_grid, containers)

            if (status is True):
                print_grid(ship_grid)

                left_balance, right_balance, balanced = calculate_balance(
                    ship_grid)

                print("Total Weight:", total_weight)
                print("Left Balance:", left_balance)
                print("Right Balance:", right_balance)
                print("Balanced!")

            print("Final Grid")
            print_grid(ship_grid)
            print()
            print("Steps:")
            print(steps)

    else:

        case = int(input("Select a load/unload case from 1 - 5: "))

        print_grid(ship_grid)
        print()

        steps, ship_grids = [], None

        # Case 1 Unload
        if case == 1:
            steps, ship_grids = unload([[0, 1]], ship_grid)

        # Case 2 Load
        if case == 2:
            steps, ship_grids = load(
                [(Container("Bat", 5432), [0, 4])], ship_grid)

        # Case 3 Load/Unload
        if case == 3:
            steps, ship_grids = load(
                [(Container("Bat", 5432), [0, 4]), (Container("Rat", 5397), [0, 5])], ship_grid)

            new_steps, new_ship_grids = unload([[0, 1]], ship_grids[-1])
            steps.append(new_steps)
            ship_grids.append(new_ship_grids)

        # Case 4 Load/Unload
        if case == 4:
            steps, ship_grids = load(
                [(Container("Nat", 6543), [1, 7])], ship_grid)

            print('Completed Loading')
            print_grid(ship_grids[-1])
            print()

            new_steps, new_ship_grids = unload([[6, 4]], ship_grids[-1])
            steps.append(new_steps)
            ship_grids.append(new_ship_grids)

        # Case 5 Load/Unload
        if case == 5:
            steps, ship_grids = load(
                [(Container("Nat", 153), [0, 7]), (Container("Rat", 2321), [0, 8])], ship_grid)

            print(steps)

            new_steps, new_ship_grids = unload(
                [[0, 4], [0, 3]], ship_grids[-1])
            for step in new_steps:
                steps.append(step)
            ship_grids.append(new_ship_grids)

        r, c = np.array(ship_grids[0]).shape
        ship_grids = reformat_grid_list(ship_grids, r, c)
        print_grid(ship_grids[-1])

        print(steps)
