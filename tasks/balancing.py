import copy
import re
import numpy as np
from collections.abc import Iterable

class Container:
    def __init__(self, name, weight):
        self.name = name
        self.weight = weight


class Slot:
    def __init__(self, container: Container, has_container, available):
        self.container = container
        self.has_container = has_container
        self.available = available


def create_ship_grid(rows, columns):
    return [[Slot(None, False, False) for _ in range(columns)] for _ in range(rows)]


def update_ship_grid(file_content, ship_grid, containers):
    """
    Updates the ship grid with data from the manifest file.
    """
    for line in file_content.splitlines():
        slot_data = line.split()
        loc = [int(val) - 1 for val in re.sub(r"[\[\]]", '', slot_data[0]).split(",")[:2]]
        weight = int(re.sub(r"[\{\}\,]", '', slot_data[1]))
        status = slot_data[2] if len(slot_data) == 3 else " ".join(slot_data[2:])
        x, y = loc

        if 0 <= x < len(ship_grid) and 0 <= y < len(ship_grid[0]):
            if status == "NAN":
                ship_grid[x][y] = Slot(None, has_container=False, available=False)
            elif status == "UNUSED":
                ship_grid[x][y] = Slot(None, has_container=False, available=True)
            else:
                ship_grid[x][y] = Slot(Container(status, weight), has_container=True, available=False)
                containers.append(loc)


def calculate_balance(ship_grid):
    """
    Calculates the left and right weight balance of the ship.
    """
    left_balance, right_balance = 0, 0
    halfway = len(ship_grid[0]) // 2

    for row in ship_grid:
        for idx, slot in enumerate(row):
            if slot.container:
                if idx < halfway:
                    left_balance += slot.container.weight
                else:
                    right_balance += slot.container.weight

    balanced = 0.9 <= left_balance / right_balance <= 1.1 if right_balance > 0 else False
    return left_balance, right_balance, balanced


def balance(ship_grid, containers):
    """
    Balances the ship by moving containers between sides.
    """
    steps, ship_grids = [], []
    left_balance, right_balance, balanced = calculate_balance(ship_grid)
    max_iterations = 100

    while not balanced and max_iterations > 0:
        side_containers = [
            loc for loc in containers if (loc[1] < len(ship_grid[0]) // 2) == (left_balance > right_balance)
        ]

        if not side_containers:
            break

        container_to_move = side_containers[0]
        goal_loc = nearest_available_balance(left_balance, right_balance, ship_grid)

        if goal_loc == (-1, -1):
            break

        step, updated_grid = move_to(container_to_move, goal_loc, ship_grid)
        steps.append(step)
        ship_grids.append(updated_grid)

        containers.remove(container_to_move)
        containers.append(goal_loc)
        left_balance, right_balance, balanced = calculate_balance(ship_grid)
        max_iterations -= 1

    return steps, ship_grids, balanced


def move_to(container_loc, goal_loc, ship_grid):
    """
    Moves a container to a new location in the ship grid.
    """
    x1, y1 = container_loc
    x2, y2 = goal_loc
    ship_grid[x2][y2].container = ship_grid[x1][y1].container
    ship_grid[x2][y2].has_container = True
    ship_grid[x2][y2].available = False
    ship_grid[x1][y1].container = None
    ship_grid[x1][y1].has_container = False
    ship_grid[x1][y1].available = True

    return f"Moved container from {container_loc} to {goal_loc}", copy.deepcopy(ship_grid)


def nearest_available_balance(left_balance, right_balance, ship_grid):
    """
    Finds the nearest available slot on the lighter side of the ship.
    """
    halfway = len(ship_grid[0]) // 2
    side = range(halfway, len(ship_grid[0])) if left_balance > right_balance else range(halfway)

    for row_idx, row in enumerate(ship_grid):
        for col_idx in side:
            if row[col_idx].available and (row_idx == 0 or not ship_grid[row_idx - 1][col_idx].available):
                return row_idx, col_idx
    return -1, -1
