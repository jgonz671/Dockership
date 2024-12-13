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
    Visualizes the ship's container grid layout using Plotly with proper text placement inside the blocks.
    Includes lighter gridlines and a less intrusive border.

    Args:
        grid (list of lists): 2D grid containing Slot objects.
        title (str): Title of the grid visualization.

    Returns:
        go.Figure: Plotly figure representing the ship grid layout.
    """
    # Ensure grid is valid before proceeding
    # validate_ship_grid(grid)

    z = []  # Color mapping for grid cells
    hover_text = []  # Hover text for each cell
    annotations = []  # Annotations for text inside cells
    shapes = []  # Manual gridline shapes

    rows = len(grid)
    cols = len(grid[0])

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

    # Add manual gridlines as shapes
    for i in range(rows + 1):  # Horizontal lines
        shapes.append(
            dict(
                type="line",
                x0=-0.5,
                y0=i - 0.5,
                x1=cols - 0.5,
                y1=i - 0.5,
                line=dict(color="rgba(0, 0, 0, 0.2)",
                          width=1),  # Lighter gridlines
            )
        )
    for j in range(cols + 1):  # Vertical lines
        shapes.append(
            dict(
                type="line",
                x0=j - 0.5,
                y0=-0.5,
                x1=j - 0.5,
                y1=rows - 0.5,
                line=dict(color="rgba(0, 0, 0, 0.2)",
                          width=1),  # Lighter gridlines
            )
        )

    # Add a border around the entire grid
    shapes.append(
        dict(
            type="rect",
            x0=-0.5,
            y0=-0.5,
            x1=cols - 0.5,
            y1=rows - 0.5,
            line=dict(color="rgba(0, 0, 0, 0.1)", width=0.1),  # Lighter border
        )
    )

    # Create the heatmap
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

    # Add annotations and shapes for gridlines
    fig.update_layout(
        title=dict(text=title, x=0.5),
        xaxis=dict(
            title="Columns",
            showgrid=False,  # Disable default gridlines
            zeroline=False,
            tickmode="array",
            tickvals=[i for i in range(cols)],
            ticktext=[f"{i + 1:02}" for i in range(cols)],
        ),
        yaxis=dict(
            title="Rows",
            showgrid=False,  # Disable default gridlines
            zeroline=False,
            tickmode="array",
            tickvals=[i for i in range(rows)],
            ticktext=[f"{i + 1:02}" for i in range(rows)],
        ),
        shapes=shapes,
        annotations=annotations,
        plot_bgcolor="white",  # Ensure the background is white for contrast
    )

    return fig
