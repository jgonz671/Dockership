# utils/visualizer.py
"""
Utility module for parsing input data and visualizing ship grid layouts.
"""

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import re
import plotly.graph_objects as go


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


def plotly_visualize_grid(grid, title="Ship Grid"):
    """
    Visualizes the ship's container grid layout using Plotly with proper text placement inside the blocks.

    Args:
        grid (list of lists): 2D grid containing Slot objects or plain text.
        title (str): Title of the plot.

    Returns:
        plotly.graph_objects.Figure: A Plotly figure object for visualization.
    """
    z = []  # Color mapping for grid cells
    hover_text = []  # Hover text for each cell
    annotations = []  # Annotations for text inside cells

    for row_idx, row in enumerate(grid):
        z_row = []
        hover_row = []
        for col_idx, slot in enumerate(row):
            manifest_coord = f"[{row_idx + 1:02},{col_idx + 1:02}]"
            if slot.container:
                cell_text = slot.container.name
                hover_info = f"Coordinates: {manifest_coord}<br>Name: {slot.container.name}<br>Weight: {slot.container.weight}"
                z_row.append(1)  # Occupied (blue)
                annotations.append(
                    dict(
                        text=cell_text,
                        x=col_idx,
                        y=row_idx,
                        xref="x",
                        yref="y",
                        showarrow=False,
                        xanchor="center",
                        yanchor="middle",
                        font=dict(size=12, color="white"),
                    )
                )
            elif not slot.available:
                cell_text = "NAN"
                hover_info = f"Coordinates: {manifest_coord}<br>NAN"
                z_row.append(-1)  # NAN (light gray)
                annotations.append(
                    dict(
                        text=cell_text,
                        x=col_idx,
                        y=row_idx,
                        xref="x",
                        yref="y",
                        showarrow=False,
                        xanchor="center",
                        yanchor="middle",
                        font=dict(size=12, color="black"),
                    )
                )
            else:
                cell_text = ""
                hover_info = f"Coordinates: {manifest_coord}<br>UNUSED"
                z_row.append(0)  # UNUSED (white)
                annotations.append(
                    dict(
                        text=cell_text,
                        x=col_idx,
                        y=row_idx,
                        xref="x",
                        yref="y",
                        showarrow=False,
                        xanchor="center",
                        yanchor="middle",
                        font=dict(size=12, color="black"),
                    )
                )
            hover_row.append(hover_info)

        z.append(z_row)
        hover_text.append(hover_row)

    fig = go.Figure(
        data=go.Heatmap(
            z=z,
            colorscale=[
                [0, "white"],       # Empty slots
                [0.5, "lightgray"],  # NAN slots
                [1, "blue"],        # Occupied slots
            ],
            hoverinfo="text",
            text=hover_text,
            showscale=False,
        )
    )
    fig.update_layout(
        title=dict(text=title, x=0.5),
        xaxis=dict(
            title="Columns",
            showgrid=False,
            zeroline=False,
            tickmode="array",
            tickvals=[i for i in range(len(grid[0]))],
            ticktext=[f"{i + 1:02}" for i in range(len(grid[0]))],
        ),
        yaxis=dict(
            title="Rows",
            showgrid=False,
            zeroline=False,
            tickmode="array",
            tickvals=[i for i in range(len(grid))],
            ticktext=[f"{i + 1:02}" for i in range(len(grid))],
        ),
        annotations=annotations,
        plot_bgcolor="white",
    )
    return fig


# def display_grid(grid, title="Grid Layout"):
#     """
#     Visualizes the ship's container grid layout with metrics.

#     Args:
#         grid (numpy.ndarray or list): The grid layout to display.
#         title (str): The title of the grid.
#     """
#     if isinstance(grid, list):  # Convert list to NumPy array if needed
#         grid = np.array(grid)

#     fig, ax = plt.subplots(figsize=(12, 8))
#     for i in range(grid.shape[0]):
#         for j in range(grid.shape[1]):
#             value = grid[i, j]
#             if value == "UNUSED":
#                 color, text = "lightgray", ""
#             elif value == "NAN":
#                 color, text = "white", "NAN"
#             else:
#                 color, text = "blue", str(value)  # Display container ID or name

#             ax.add_patch(plt.Rectangle((j, i), 1, 1, facecolor=color, edgecolor="black"))
#             ax.text(
#                 j + 0.5, i + 0.5, text,
#                 ha="center", va="center",
#                 fontsize=10, color="white" if color == "blue" else "black"
#             )

#     ax.set_xlim(0, grid.shape[1])
#     ax.set_ylim(0, grid.shape[0])
#     ax.invert_yaxis()
#     plt.title(title)
#     st.pyplot(fig)


# def convert_to_display_grid(ship_grid):
#     """
#     Converts a ship grid with Slot objects to a NumPy array for visualization.

#     Args:
#         ship_grid (list of lists): Ship grid with Slot objects.

#     Returns:
#         np.ndarray: 2D array ready for visualization.
#     """
#     display_grid = np.empty((len(ship_grid), len(ship_grid[0])), dtype=object)

#     for i, row in enumerate(ship_grid):
#         for j, slot in enumerate(row):
#             if slot.container:
#                 display_grid[i, j] = slot.container.name
#             elif slot.available:
#                 display_grid[i, j] = "UNUSED"
#             else:
#                 display_grid[i, j] = "NAN"

#     return display_grid

