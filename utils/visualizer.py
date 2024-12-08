# utils/visualizer.py
"""
Utility module for parsing input data and visualizing ship grid layouts.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import re


def parse_input(input_lines, rows=8, cols=12):
    """
    Parses input data into a grid format.

    Args:
        input_lines (list): List of input lines from the manifest file.
        rows (int): Number of rows in the grid.
        cols (int): Number of columns in the grid.

    Returns:
        numpy.ndarray: Parsed grid layout.
    """
    grid = np.full((rows, cols), "UNUSED", dtype=object)
    line_regex = re.compile(r"\[(\d+),(\d+)\]\s*,\s*\{\d+\}\s*,\s*(\w+)")

    for line in input_lines:
        line = line.strip()
        if not line:  # Skip empty lines
            continue

        # Match line format
        match = line_regex.match(line)
        if match:
            row, col, container = match.groups()
            row, col = int(row), int(col)

            # Convert coordinates to grid indices
            grid_row = rows - row  # Reverse row indexing for grid
            grid_col = col - 1  # Convert 1-based to 0-based indexing

            if 0 <= grid_row < rows and 0 <= grid_col < cols:
                grid[grid_row, grid_col] = container

    return grid



def display_grid(grid, title="Grid Layout"):
    """
    Visualizes the ship's container grid layout with metrics.

    Args:
        grid (numpy.ndarray): The grid layout to display.
        title (str): The title of the grid.
    """
    if isinstance(grid, list):  # Convert list to NumPy array if needed
        grid = np.array(grid)

    fig, ax = plt.subplots(figsize=(12, 8))
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            value = grid[i, j]
            if value == "UNUSED":
                color, text = "lightgray", ""
            elif value == "NAN":
                color, text = "white", "NAN"
            else:
                color, text = "blue", str(value)  # Display container ID or name

            ax.add_patch(plt.Rectangle((j, i), 1, 1, facecolor=color, edgecolor="black"))
            ax.text(
                j + 0.5, i + 0.5, text,
                ha="center", va="center",
                fontsize=8, color="white"
            )

    ax.set_xlim(0, grid.shape[1])
    ax.set_ylim(0, grid.shape[0])
    ax.invert_yaxis()
    plt.title(title)
    st.pyplot(fig)


