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
    """
    grid = np.full((rows, cols), np.nan, dtype=object)
    line_regex = re.compile(r"\[(\d+),(\d+)\]\s*,\s*\{\d+\}\s*,\s*(\w+)")
    for line in input_lines:
        match = line_regex.match(line)
        if match:
            row, col, container = match.groups()
            row, col = rows - int(row), int(col) - 1
            if 0 <= row < rows and 0 <= col < cols:
                grid[row, col] = container if container != "NAN" else np.nan
    return grid


def display_grid(grid, title="Grid Layout"):
    """
    Visualizes the ship's container grid layout.
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            value = grid[i, j]
            color, text = ("lightgray", "NAN") if pd.isna(value) else (
                "white", ""
            ) if value == "UNUSED" else ("blue", value)
            ax.add_patch(plt.Rectangle(
                (j, i), 1, 1, facecolor=color, edgecolor="black"))
            ax.text(j + 0.5, i + 0.5, text, ha="center",
                    va="center", fontsize=10)
    ax.set_xlim(0, grid.shape[1])
    ax.set_ylim(0, grid.shape[0])
    ax.invert_yaxis()
    plt.title(title)
    st.pyplot(fig)
