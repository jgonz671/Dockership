# utils/grid_utils.py
from tasks.ship_balancer import Slot, Container
from utils.validators import validate_ship_grid
import plotly.graph_objects as go


def create_ship_grid(rows, columns):
    """
    Creates a ship grid with the specified number of rows and columns.

    Args:
        rows (int): Number of rows in the grid.
        columns (int): Number of columns in the grid.

    Returns:
        list: A 2D grid (list of lists) containing Slot objects.
    """
    return [[Slot(None, False, False) for _ in range(columns)] for _ in range(rows)]


def plotly_visualize_grid(grid, title="Ship Grid"):
    """
    Visualizes the ship's container grid layout using Plotly.

    Args:
        grid (list of lists): 2D grid containing Slot objects.
        title (str): Title of the plot.

    Returns:
        plotly.graph_objects.Figure: A Plotly figure object for visualization.
    """
    validate_ship_grid(grid)

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
