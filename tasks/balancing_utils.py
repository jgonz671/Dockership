import streamlit as st
import plotly.graph_objects as go
from copy import deepcopy
from tasks.ship_balancer import (
    create_ship_grid,
    update_ship_grid,
    Container,
    Slot,
    calculate_balance,
    balance,
)
import os

def plotly_visualize_grid(grid, title="Ship Grid"):
    """
    Visualizes the ship's container grid layout using Plotly with proper text placement inside the blocks.
    Includes lighter gridlines and a less intrusive border.
    """
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
    # Create manual gridlines as shapes
    for i in range(rows + 1):  # Horizontal lines
        shapes.append(
            dict(
                type="line",
                x0=-0.5,
                y0=i - 0.5,
                x1=cols - 0.5,
                y1=i - 0.5,
                line=dict(color="rgba(0, 0, 0, 0.2)", width=1),  # Lighter gridlines
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
                line=dict(color="rgba(0, 0, 0, 0.2)", width=1),  # Lighter gridlines
            )
        )
    # Add a border around the entire grid with lighter color and reduced width
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
                [0.5, "lightgray"], # NAN slots
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
        shapes=shapes,  # Add manual gridlines
        annotations=annotations,
        plot_bgcolor="black",  # Ensure the background is white for contrast
    )
    return fig
def convert_grid_to_manifest(ship_grid):
    """
    Converts the updated grid back to manifest format.
    Args:
        ship_grid (list): The ship grid with Slot objects.
    Returns:
        str: manifest string representing the updated grid.
    """
    manifest_lines = []
    for row_idx, row in enumerate(ship_grid):
        for col_idx, slot in enumerate(row):
            coordinates = f"[{row_idx + 1:02},{col_idx + 1:02}]"  # Row, Column coordinates
            weight = f"{{{slot.container.weight:05}}}" if slot.container else "{00000}"  # Weight with 5 digits
            status_or_name = slot.container.name if slot.container else ("NAN" if not slot.available else "UNUSED")  # Name, NAN, or UNUSED
            line = f"{coordinates}, {weight}, {status_or_name}"
            manifest_lines.append(line)
    return "\n".join(manifest_lines)


def append_outbound_to_filename(filename):
    """
    Appends 'OUTBOUND' to the filename before the extension.
    Args:
        filename (str): Original filename.
    Returns:
        str: Updated filename with 'OUTBOUND' appended.
    """
    name, ext = os.path.splitext(filename)
    return f"{name}_OUTBOUND{ext}"
def plotly_visualize_grid_with_overlay(grid, from_coords, to_coords, title="Ship Grid"):
    """
    Visualizes the ship's container grid layout with an overlay for sub-step movements.
    
    Args:
        grid (list): The base grid to visualize.
        from_coords (tuple): Coordinates of the source (red highlight).
        to_coords (tuple): Coordinates of the destination (green highlight).
        title (str): Title for the plot.
    """
    z = []  # Color mapping for grid cells
    annotations = []  # Annotations for text inside cells
    shapes = []  # Gridlines
    rows = len(grid)
    cols = len(grid[0])
    moved_container_name = None  # Track the name of the container being moved
    for row_idx, row in enumerate(grid):
        z_row = []
        for col_idx, slot in enumerate(row):
            if (row_idx, col_idx) == (from_coords[0], from_coords[1]):
                z_row.append(2)  # Source (red highlight)
                moved_container_name = slot.container.name if slot.container else "N/A"
            elif (row_idx, col_idx) == (to_coords[0], to_coords[1]):
                z_row.append(3)  # Destination (green highlight)
            elif slot.container:
                z_row.append(1)  # Occupied (blue)
            elif not slot.available:
                z_row.append(-1)  # NAN (light gray)
            else:
                z_row.append(0)  # UNUSED (white)
            # Add annotation text for the cell
            if slot.container:
                text = slot.container.name  # Container name
                color = "white"
            elif not slot.available:
                text = "NAN"
                color = "black"
            else:
                text = ""
                color = "black"
            annotations.append(
                dict(
                    text=text,
                    x=col_idx,
                    y=row_idx,
                    xref="x",
                    yref="y",
                    showarrow=False,
                    xanchor="center",
                    yanchor="middle",
                    font=dict(size=12, color=color),
                )
            )
        z.append(z_row)
    # Add annotation for the red block (source)
    if moved_container_name:
        annotations.append(
            dict(
                text=moved_container_name,
                x=from_coords[1],
                y=from_coords[0],
                xref="x",
                yref="y",
                showarrow=False,
                xanchor="center",
                yanchor="middle",
                font=dict(size=12, color="white"),
            )
        )
    # Add gridlines to the plot
    for i in range(rows + 1):  # Horizontal lines
        shapes.append(
            dict(
                type="line",
                x0=-0.5,
                y0=i - 0.5,
                x1=cols - 0.5,
                y1=i - 0.5,
                line=dict(color="rgba(0, 0, 0, 0.2)", width=1),  # Semi-transparent gridlines
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
                line=dict(color="rgba(0, 0, 0, 0.2)", width=1),  # Semi-transparent gridlines
            )
        )
    # Create the heatmap with normalized colorscale values
    fig = go.Figure(
        data=go.Heatmap(
            z=z,
            colorscale=[
                [0, "white"],        # Empty slots
                [0.25, "lightgray"], # NAN slots
                [0.5, "blue"],       # Occupied slots
                [0.75, "red"],       # Source (highlight)
                [1, "green"],        # Destination (highlight)
            ],
            showscale=False,
        )
    )
    # Add annotations and gridlines to the plot
    fig.update_layout(
        title=dict(text=title, x=0.5),
        xaxis=dict(
            title="Columns",
            tickvals=[i for i in range(cols)],
            ticktext=[f"{i + 1:02}" for i in range(cols)],
        ),
        yaxis=dict(
            title="Rows",
            tickvals=[i for i in range(rows)],
            ticktext=[f"{i + 1:02}" for i in range(rows)],
        ),
        shapes=shapes,  # Add gridlines
        annotations=annotations,
        plot_bgcolor="white",
    )
    return fig
def generate_animation_with_annotations():
    """
    Generates a single Plotly animation for the balancing steps with annotations for each sub-step.
    """
    if "steps" in st.session_state and "ship_grids" in st.session_state:
        st.subheader("Animation of Steps")
        # Initialize figure
        fig = go.Figure()
        # Initial grid setup
        initial_grid = st.session_state.initial_grid
        frames = []  # To store each animation frame
        # Gridline shapes for overlay
        rows = len(initial_grid)
        cols = len(initial_grid[0])
        gridline_shapes = []
        for i in range(rows + 1):  # Horizontal gridlines
            gridline_shapes.append(
                dict(
                    type="line",
                    x0=-0.5,
                    y0=i - 0.5,
                    x1=cols - 0.5,
                    y1=i - 0.5,
                    line=dict(color="rgba(0, 0, 0, 0.5)", width=1),  # Semi-transparent black lines
                )
            )
        for j in range(cols + 1):  # Vertical gridlines
            gridline_shapes.append(
                dict(
                    type="line",
                    x0=j - 0.5,
                    y0=-0.5,
                    x1=j - 0.5,
                    y1=rows - 0.5,
                    line=dict(color="rgba(0, 0, 0, 0.5)", width=1),  # Semi-transparent black lines
                )
            )
        # Iterate through steps and sub-steps
        for step_index, step in enumerate(st.session_state.steps):
            base_grid = (
                st.session_state.ship_grids[step_index - 1]
                if step_index > 0
                else st.session_state.initial_grid
            )
            for sub_step in step:
                # Parse coordinates
                from_coords, to_coords = sub_step.replace("[", "").replace("]", "").split(" to ")
                from_x, from_y = map(int, from_coords.split(","))
                to_x, to_y = map(int, to_coords.split(","))
                # Prepare z values and annotations for this frame
                z_frame = []
                annotations_frame = []
                for row_idx, row in enumerate(base_grid):
                    z_row = []
                    for col_idx, slot in enumerate(row):
                        if (row_idx, col_idx) == (from_x, from_y):
                            z_row.append(2)  # Source (red highlight)
                            annotations_frame.append(
                                dict(
                                    text=slot.container.name if slot.container else "N/A",
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
                        elif (row_idx, col_idx) == (to_x, to_y):
                            z_row.append(3)  # Destination (green highlight)
                        elif slot.container:
                            z_row.append(1)  # Occupied (blue)
                            annotations_frame.append(
                                dict(
                                    text=slot.container.name,
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
                            z_row.append(-1)  # NAN (light gray)
                            annotations_frame.append(
                                dict(
                                    text="NAN",
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
                            z_row.append(0)  # Unused (white)
                    z_frame.append(z_row)
                # Append the frame
                frames.append(
                    go.Frame(
                        data=[go.Heatmap(
                            z=z_frame,
                            colorscale=[
                                [0, "white"],
                                [0.25, "lightgray"],
                                [0.5, "blue"],
                                [0.75, "red"],
                                [1, "green"],
                            ],
                            showscale=False,
                        )],
                        layout=go.Layout(annotations=annotations_frame, shapes=gridline_shapes),
                    )
                )
        # Add initial frame to the figure
        fig.add_trace(frames[0].data[0])
        fig.update_layout(annotations=frames[0].layout.annotations)
        # Add frames to the figure
        fig.frames = frames
        # Add play/pause buttons
        fig.update_layout(
            updatemenus=[
                dict(
                    type="buttons",
                    showactive=False,
                    buttons=[
                        dict(
                            label="Play",
                            method="animate",
                            args=[None, dict(frame=dict(duration=500, redraw=True), fromcurrent=True)],
                        ),
                        dict(
                            label="Pause",
                            method="animate",
                            args=[[None], dict(frame=dict(duration=0, redraw=False))],
                        ),
                    ],
                )
            ]
        )
        # Set axis titles and gridlines
        fig.update_layout(
            xaxis=dict(
                tickvals=[i for i in range(cols)],
                ticktext=[f"{i + 1:02}" for i in range(cols)],
            ),
            yaxis=dict(
                tickvals=[i for i in range(rows)],
                ticktext=[f"{i + 1:02}" for i in range(rows)],
            ),
        )
        # Display the animation
        st.plotly_chart(fig, use_container_width=True)
        
def generate_stepwise_animation(initial_grid, steps, ship_grids):
    
    frames = []
    base_grid = deepcopy(initial_grid)
    # Add a frame for each step and sub-step
    for step_idx, (step, step_grid) in enumerate(zip(steps, ship_grids)):
        for sub_step_idx, sub_step in enumerate(step):
            from_coords, to_coords = sub_step.replace("[", "").replace("]", "").split(" to ")
            from_x, from_y = map(int, from_coords.split(","))
            to_x, to_y = map(int, to_coords.split(","))
            # Create the plot for this sub-step
            frame_fig = plotly_visualize_grid_with_overlay(
                base_grid, (from_x, from_y), (to_x, to_y),
                title=f"Step {step_idx + 1}, Sub-Step {sub_step_idx + 1}"
            )
            # Add the frame to the animation
            frames.append(
                go.Frame(
                    data=frame_fig.data,
                    name=f"step_{step_idx}_substep_{sub_step_idx}",
                )
            )
        # Update base grid to the final state of the current step
        base_grid = deepcopy(step_grid)
    # Create the main figure
    fig = go.Figure(
        data=frames[0].data if frames else [],
        layout=frames[0].layout if frames else {},
    )
    # Add frames to the figure
    fig.frames = frames
    # Add Play/Pause buttons for animation
    fig.update_layout(
        updatemenus=[
            {
                "buttons": [
                    {
                        "args": [None, {"frame": {"duration": 500, "redraw": True}, "fromcurrent": True}],
                        "label": "Play",
                        "method": "animate",
                    },
                    {
                        "args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate"}],
                        "label": "Pause",
                        "method": "animate",
                    },
                ],
                "direction": "left",
                "pad": {"r": 10, "t": 87},
                "showactive": False,
                "type": "buttons",
                "x": 0.1,
                "xanchor": "right",
                "y": 0,
                "yanchor": "top",
            }
        ]
    )
    return fig