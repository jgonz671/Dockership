# pages/components/grid.py
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def display_grid(grid, title="Grid Layout"):
    """
    Visualizes the ship's container grid layout.

    Args:
        grid (numpy.ndarray): The grid layout to display.
        title (str): The title of the grid.
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            value = grid[i, j]
            color, text = ("lightgray", "NAN") if pd.isna(value) else (
                "white", "" ) if value == "UNUSED" else ("blue", value)
            ax.add_patch(plt.Rectangle(
                (j, i), 1, 1, facecolor=color, edgecolor="black"))
            ax.text(j + 0.5, i + 0.5, text, ha="center",
                    va="center", fontsize=10)
    ax.set_xlim(0, grid.shape[1])
    ax.set_ylim(0, grid.shape[0])
    ax.invert_yaxis()
    plt.title(title)
    st.pyplot(fig)

def create_grid_layout(rows, cols, default_value=np.nan):
    """
    Creates a grid with the specified rows and columns, filled with a default value.

    Args:
        rows (int): The number of rows in the grid.
        cols (int): The number of columns in the grid.
        default_value (optional): The default value to fill in the grid (default is NaN).

    Returns:
        numpy.ndarray: The generated grid.
    """
    return np.full((rows, cols), default_value, dtype=object)

