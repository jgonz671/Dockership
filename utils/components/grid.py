import numpy as np

def create_grid_layout(rows, cols, default_value="UNUSED"):
    """
    Creates a grid with the specified rows and columns, filled with a default value.

    Args:
        rows (int): The number of rows in the grid.
        cols (int): The number of columns in the grid.
        default_value (str): The default value to fill in the grid (e.g., "UNUSED").

    Returns:
        numpy.ndarray: The generated grid.
    """
    return np.full((rows, cols), default_value, dtype=object)
