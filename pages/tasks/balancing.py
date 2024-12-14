import streamlit as st
import plotly.graph_objects as go
from copy import deepcopy
from utils.components.buttons import create_button, create_navigation_button
from tasks.ship_balancer import (
    create_ship_grid,
    update_ship_grid,
    Container,
    Slot,
    calculate_balance,
    balance,
)

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
def convert_grid_to_manuscript(ship_grid):
    """
    Converts the updated grid back to manuscript format.
    Args:
        ship_grid (list): The ship grid with Slot objects.
    Returns:
        str: Manuscript string representing the updated grid.
    """
    manuscript_lines = []
    for row_idx, row in enumerate(ship_grid):
        for col_idx, slot in enumerate(row):
            coordinates = f"[{row_idx + 1:02},{col_idx + 1:02}]"  # Row, Column coordinates
            weight = f"{{{slot.container.weight:05}}}" if slot.container else "{00000}"  # Weight with 5 digits
            status_or_name = slot.container.name if slot.container else ("NAN" if not slot.available else "UNUSED")  # Name, NAN, or UNUSED
            line = f"{coordinates}, {weight}, {status_or_name}"
            manuscript_lines.append(line)
    return "\n".join(manuscript_lines)
import os
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

def plotly_visualize_grid_dynamic(grid, title="Ship Grid", highlight=None):
    """
    Visualizes the ship's container grid layout using Plotly with proper text placement inside the blocks.
    Includes lighter gridlines and highlights the specific container being moved.
    
    Args:
        grid (list): The ship grid to visualize.
        title (str): Title of the grid visualization.
        highlight (tuple): Tuple containing (from_coords, to_coords) to highlight a container's movement.
    """
    z = []  # Color mapping for grid cells
    hover_text = []  # Hover text for each cell
    annotations = []  # Annotations for text inside cells
    shapes = []  # Manual gridline shapes
    rows = len(grid)
    cols = len(grid[0])
    highlight_from, highlight_to = highlight if highlight else (None, None)
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
    # Highlight the specific container's movement
    if highlight_from:
        shapes.append(
            dict(
                type="rect",
                x0=highlight_from[1] - 0.5,
                y0=highlight_from[0] - 0.5,
                x1=highlight_from[1] + 0.5,
                y1=highlight_from[0] + 0.5,
                line=dict(color="red", width=2),  # Highlight source in red
            )
        )
    if highlight_to:
        shapes.append(
            dict(
                type="rect",
                x0=highlight_to[1] - 0.5,
                y0=highlight_to[0] - 0.5,
                x1=highlight_to[1] + 0.5,
                y1=highlight_to[0] + 0.5,
                line=dict(color="green", width=2),  # Highlight target in green
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
def visualize_steps_with_overlay():
    """
    Visualize the base grid for the selected step and overlay it with sub-step movements.
    """
    if "steps" in st.session_state and "ship_grids" in st.session_state:
        st.subheader("Steps with Sub-Step Movement Overlay")
        # Ensure the initial grid is set once
        if "initial_grid" not in st.session_state:
            # Make a deep copy of the initial grid to ensure it's not inadvertently modified
            st.session_state.initial_grid = [row[:] for row in st.session_state.ship_grid]
        # Select Step
        total_steps = len(st.session_state.steps)
        step_number = st.number_input("Select Step", min_value=1, max_value=total_steps, value=1, step=1) - 1
        # Base grid for the selected step
        base_grid = (
            st.session_state.initial_grid
            if step_number == 0
            else st.session_state.ship_grids[step_number - 1]
        )
        #base_grid_plot = plotly_visualize_grid(base_grid, title=f"Base Grid for Step {step_number + 1}")
        # Display base grid
        #st.plotly_chart(base_grid_plot, use_container_width=True)
        # Select Sub-Step
        selected_step = st.session_state.steps[step_number]
        total_sub_steps = len(selected_step)
        sub_step_number = st.number_input(
            "Select Sub-Step", min_value=1, max_value=total_sub_steps, value=1, step=1
        ) - 1
        # Get current sub-step details
        current_sub_step = selected_step[sub_step_number]
        from_coords, to_coords = current_sub_step.replace("[", "").replace("]", "").split(" to ")
        from_x, from_y = map(int, from_coords.split(","))
        to_x, to_y = map(int, to_coords.split(","))
        # Overlay the sub-step movement on the base grid
        overlay_plot = plotly_visualize_grid_with_overlay(
            base_grid, (from_x, from_y), (to_x, to_y), title="Step with Sub-Step Movement Overlay"
        )
        st.plotly_chart(overlay_plot, use_container_width=True)
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
    """
    Generates an animation for the ship balancing steps, displaying each sub-step within each step sequentially.
    
    Args:
        initial_grid (list): The initial grid of the ship.
        steps (list): List of steps with sub-steps.
        ship_grids (list): List of grids representing the ship state after each step.
    
    Returns:
        Plotly figure with animation frames.
    """
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
def balancing_page():
    # Streamlit App
    col1, _ = st.columns([2, 8])  # Center the button
    with col1:
        if create_navigation_button("Back to Operations", "operation", st.session_state):
            st.rerun() 
    st.title("Ship Balancing Project")
    # Sidebar for grid setup
    st.sidebar.header("Ship Grid Setup")
    rows = 8  # Fixed to match the manifest
    columns = 12  # Fixed to match the manifest
    if "steps" not in st.session_state:
        st.session_state["steps"] = []
        
    # if "ship_grids" not in st.session_state:  # Ensure ship_grids is initialized
    #     st.session_state["ship_grids"] = []
    if "final_plot" not in st.session_state:
        st.session_state.final_plot = None
        
    # Initialize session state
    if "ship_grid" not in st.session_state:
        st.session_state.ship_grid = create_ship_grid(rows, columns)
        st.session_state.containers = []
        st.session_state.initial_plot = None
        st.session_state.final_plot = None
        st.session_state.steps = []
        st.session_state.ship_grids = []  # Store grids for steps visualization
    # Use manuscript from file_handler
    if "file_content" in st.session_state:
        try:
            # Use file content from file_handler
            file_content = st.session_state["file_content"].splitlines()
            update_ship_grid(file_content, st.session_state.ship_grid, st.session_state.containers)
            st.session_state.initial_plot = plotly_visualize_grid(
                st.session_state.ship_grid, title="Initial Ship Grid"
            )
            st.success("Ship grid updated successfully from manuscript.")
        except Exception as e:
            st.error(f"Error processing the manuscript: {e}")
    else:
        st.error("No manuscript available. Please upload a file in the File Handler page.")
    # Display initial grid
    if st.session_state.initial_plot:
        st.subheader("Initial Ship Grid")
        st.plotly_chart(st.session_state.initial_plot)
    
    # Perform balancing
    if st.button("Balance Ship"):
        # Save the initial grid only once to preserve its state
        if "initial_grid" not in st.session_state:
            st.session_state["initial_grid"] = [row.copy() for row in st.session_state.ship_grid]
        # Calculate balance and perform balancing
        left_balance, right_balance, balanced = calculate_balance(st.session_state.ship_grid)
        if balanced:
            st.success("The ship is already balanced!")
        else:
            steps, ship_grids, status = balance(st.session_state.ship_grid, st.session_state.containers)
            st.session_state.steps = steps
            st.session_state.ship_grids = ship_grids  # Store intermediate grids
            st.session_state.ship_grid = ship_grids[-1]
            st.session_state.final_plot = plotly_visualize_grid(
                st.session_state.ship_grid, title="Final Ship Grid After Balancing"
            )
            if status:
                st.success("Ship balanced successfully!")
            else:
                st.warning("Ship could not be perfectly balanced. Check balancing steps.")
    # Tabs for navigation
    selected_tab = st.radio(
        "Choose a tab",
        ["Steps", "Steps with Grids", "Steps Summary", "Block Movement Animation"],
        horizontal=True
    )
    if selected_tab == "Steps":
        # Display balancing steps
        if st.session_state.steps:
            st.subheader("Balancing Steps")
            for step_number, step_list in enumerate(st.session_state.steps):
                st.markdown(f"**Step {step_number + 1}:**")
                for sub_step_number, sub_step in enumerate(step_list):
                    # Parse and increment the coordinates
                    original_step = sub_step.replace("[", "").replace("]", "")  # Remove brackets for processing
                    from_coords, to_coords = original_step.split(" to ")   # Split into 'from' and 'to' parts
                    from_x, from_y = map(int, from_coords.split(","))
                    to_x, to_y = map(int, to_coords.split(","))
                    # Increment the coordinates
                    from_x += 1
                    from_y += 1
                    to_x += 1
                    to_y += 1
                    # Format back into the desired string
                    incremented_step = f"[{from_x},{from_y}] to [{to_x},{to_y}]"
                    st.write(f"{sub_step_number + 1}. {incremented_step}")
    elif selected_tab == "Steps with Grids":
        #visualize_steps_with_grids()
        visualize_steps_with_overlay()
    
    elif selected_tab == "Block Movement Animation":
        # Animation for all steps
        generate_animation_with_annotations()
    
    elif selected_tab == "Steps Summary":
        """
        Summarize movements and include plots for summarized steps.
        """
        if "steps" in st.session_state and "ship_grids" in st.session_state:
            st.subheader("Summarized Steps with Plots")
            def summarize_steps(steps):
                """
                Summarizes a list of steps by collapsing consecutive movements into a single range.
                Args:
                    steps (list): List of step lists containing movements as strings.
                Returns:
                    list: Summarized steps.
                """
                summarized_steps = []
                for step_number, step_list in enumerate(steps):
                    if not step_list:
                        continue
                    start_coords = None
                    end_coords = None
                    for sub_step in step_list:
                        # Parse the coordinates
                        from_coords, to_coords = sub_step.replace("[", "").replace("]", "").split(" to ")
                        from_x, from_y = map(int, from_coords.split(","))
                        to_x, to_y = map(int, to_coords.split(","))
                        if start_coords is None:
                            start_coords = (from_x + 1, from_y + 1)  # Convert to 1-based index
                        end_coords = (to_x + 1, to_y + 1)  # Update the latest destination
                    summarized_steps.append(f"[{start_coords[0]},{start_coords[1]}] to [{end_coords[0]},{end_coords[1]}]")
                return summarized_steps
            # Summarize the steps
            summarized_steps = summarize_steps(st.session_state.steps)
            # Display summarized steps with plots
            for step_number, summary in enumerate(summarized_steps):
                st.markdown(f"### Step {step_number + 1}: {summary}")
                # Extract start and end coordinates
                start_coords, end_coords = summary.split(" to ")
                start_x, start_y = map(int, start_coords.replace("[", "").replace("]", "").split(","))
                end_x, end_y = map(int, end_coords.replace("[", "").replace("]", "").split(","))
                # Get the base grid for this step
                base_grid = (
                    st.session_state.ship_grids[step_number - 1]
                    if step_number > 0
                    else st.session_state.initial_grid
                )
                # Create a plot for this step
                def plot_grid_with_summary(grid, start, end):
                    z = []
                    annotations = []
                    for row_idx, row in enumerate(grid):
                        z_row = []
                        for col_idx, slot in enumerate(row):
                            if (row_idx, col_idx) == (start[0] - 1, start[1] - 1):  # Convert back to 0-based index
                                z_row.append(2)  # Starting position (semi-transparent red)
                                if slot.container:
                                    annotations.append(
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
                            elif (row_idx, col_idx) == (end[0] - 1, end[1] - 1):  # Convert back to 0-based index
                                z_row.append(3)  # Ending position (green)
                                annotations.append(
                                    dict(
                                        text="End",
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
                            elif slot.container:
                                z_row.append(1)  # Occupied
                                annotations.append(
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
                                z_row.append(-1)  # NAN
                            else:
                                z_row.append(0)  # Empty
                        z.append(z_row)
                    fig = go.Figure(
                        data=go.Heatmap(
                            z=z,
                            colorscale=[
                                [0, "rgba(255, 255, 255, 1.0)"],  # Empty (White)
                                [0.25, "rgba(211, 211, 211, 1.0)"],  # NAN (Light Gray)
                                [0.5, "rgba(0, 0, 255, 1.0)"],  # Occupied (Blue)
                                [0.75, "rgba(255, 0, 0, 0.5)"],  # Semi-Transparent Red for Start
                                [1, "rgba(0, 255, 0, 1.0)"],  # Green for End
                            ],
                            showscale=False,
                        )
                    )
                    fig.update_layout(
                        annotations=annotations,
                        xaxis=dict(
                            tickvals=[i for i in range(len(grid[0]))],
                            ticktext=[f"{i + 1:02}" for i in range(len(grid[0]))],
                        ),
                        yaxis=dict(
                            tickvals=[i for i in range(len(grid))],
                            ticktext=[f"{i + 1:02}" for i in range(len(grid))],
                        ),
                    )
                    return fig
                # Plot for this summarized step
                plot = plot_grid_with_summary(base_grid, (start_x, start_y), (end_x, end_y))
                st.plotly_chart(plot, use_container_width=True)

        
    # Display final grid after balancing
    if st.session_state.final_plot:
        st.subheader("Final Ship Grid After Balancing")
        st.plotly_chart(st.session_state.final_plot)
        # Generate updated manuscript
        updated_manuscript = convert_grid_to_manuscript(st.session_state.ship_grid)
        outbound_filename = append_outbound_to_filename(st.session_state.get("file_name", "manuscript.txt"))
        # Provide download button
        st.download_button(
            label="Download Updated Manuscript",
            data=updated_manuscript,
            file_name=outbound_filename,
            mime="text/plain",
        )
