import streamlit as st
import plotly.graph_objects as go
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
                [0.5, "lightgray"], # NAN slots
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
def balancing_page():
    # Streamlit App
    st.title("Ship Balancing Project")

    # Sidebar for grid setup
    st.sidebar.header("Ship Grid Setup")
    rows = 8  # Fixed to match the manifest
    columns = 12  # Fixed to match the manifest
    
    if "steps" not in st.session_state:
        st.session_state["steps"] = []
        
    if "final_plot" not in st.session_state:
        st.session_state.final_plot = None

    # Initialize session state
    if "ship_grid" not in st.session_state:
        st.session_state.ship_grid = create_ship_grid(rows, columns)
        st.session_state.containers = []
        st.session_state.initial_plot = None
        st.session_state.final_plot = None
        st.session_state.steps = []

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
        left_balance, right_balance, balanced = calculate_balance(st.session_state.ship_grid)
        if balanced:
            st.success("The ship is already balanced!")
        else:
            steps, ship_grids, status = balance(st.session_state.ship_grid, st.session_state.containers)
            st.session_state.steps = steps
            st.session_state.ship_grid = ship_grids[-1]
            st.session_state.final_plot = plotly_visualize_grid(
                st.session_state.ship_grid, title="Final Ship Grid After Balancing"
            )
            if status:
                st.success("Ship balanced successfully!")
            else:
                st.warning("Ship could not be perfectly balanced. Check balancing steps.")

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



    # Display final grid after balancing
    if st.session_state.final_plot:
        st.subheader("Final Ship Grid After Balancing")
        st.plotly_chart(st.session_state.final_plot)

'''

import streamlit as st
from tasks.balancing import balance, calculate_balance
from utils.visualizer import display_grid

# Changes 1
import streamlit as st
import plotly.graph_objects as go
from tasks.ship_balancer import (
    create_ship_grid,
    update_ship_grid,
    Container,
    Slot,
    calculate_balance,
    balance,
)

def convert_to_display_grid(ship_grid):
    """
    Converts the ship grid (list of Slot objects) to a NumPy array for visualization.

    Args:
        ship_grid (list): The ship grid with Slot objects.

    Returns:
        numpy.ndarray: Grid ready for visualization.
    """
    import numpy as np
    visual_grid = np.empty((len(ship_grid), len(ship_grid[0])), dtype=object)

    for i, row in enumerate(ship_grid):
        for j, slot in enumerate(row):
            if slot.container:
                visual_grid[i, j] = slot.container.name
            elif slot.available:
                visual_grid[i, j] = "UNUSED"
            else:
                visual_grid[i, j] = "NAN"

    return visual_grid


# Changes 2 

def plotly_visualize_grid(grid, title="Ship Grid"):
    """
    Visualizes the ship's container grid layout using Plotly with proper text placement inside the blocks.
    """
    import plotly.graph_objects as go

    z = []  # Color mapping for grid cells
    hover_text = []  # Hover text for each cell
    annotations = []  # Annotations for text inside cells

    # Iterate through the grid
    for row_idx, row in enumerate(grid):
        z_row = []
        hover_row = []
        for col_idx, slot in enumerate(row):
            # Manifest-like coordinates
            manifest_coord = f"[{row_idx + 1:02},{col_idx + 1:02}]"

            if slot.container:
                cell_text = slot.container.name
                hover_info = f"Coordinates: {manifest_coord}<br>Name: {slot.container.name}<br>Weight: {slot.container.weight}"
                z_row.append(1)  # Occupied (blue)

                # Add annotation for an occupied cell
                annotations.append(
                    dict(
                        text=cell_text,
                        x=col_idx,
                        y=row_idx,  # Correct alignment for heatmap
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

                # Add annotation for a NAN cell
                annotations.append(
                    dict(
                        text=cell_text,
                        x=col_idx,
                        y=row_idx,  # Correct alignment for heatmap
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

                # Add annotation for an unused cell
                annotations.append(
                    dict(
                        text=cell_text,
                        x=col_idx + 0.5,
                        y=row_idx + 0.5,  # Correct alignment for heatmap
                        xref="x",
                        yref="y",
                        showarrow=False,
                        xanchor="center",
                        yanchor="middle",
                        font=dict(size=12, color="black"),
                    )
                )

            # Add hover text for the current cell
            hover_row.append(hover_info)

        z.append(z_row)
        hover_text.append(hover_row)

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
            showscale=False,  # Disable the color scale
        )
    )

    # Update layout to include grid alignment and cleaner design
    fig.update_layout(
        title=dict(text=title, x=0.5),  # Center the title
        xaxis=dict(
            title="Columns",
            showgrid=False,
            zeroline=False,
            tickmode="array",
            tickvals=[i for i in range(len(grid[0]))],  # Align ticks with cells
            ticktext=[f"{i + 1:02}" for i in range(len(grid[0]))],
        ),
        yaxis=dict(
            title="Rows",
            showgrid=False,
            zeroline=False,
            tickmode="array",
            tickvals=[i for i in range(len(grid))],  # Align ticks with cells
            ticktext=[f"{i + 1:02}" for i in range(len(grid))],
        ),
        annotations=annotations,  # Add the cell text annotations
        plot_bgcolor="white",  # Set the plot background to white
    )

    return fig

def balancing_page():
    st.title("Ship Balancing Project")
    # Sidebar for grid setup
    st.sidebar.header("Ship Grid Setup")
    rows = 8  # Fixed to match the manifest
    columns = 12  # Fixed to match the manifest

    # Initialize session state
    if "ship_grid" not in st.session_state:
        st.session_state.ship_grid = create_ship_grid(rows, columns)
        st.session_state.containers = []
        st.session_state.initial_plot = None  # Save plot for initial grid
        st.session_state.final_plot = None   # Save plot for final grid after balancing
        st.session_state.steps = []  # Save balancing steps

    # File Upload for Manifest
    st.sidebar.header("Upload Manifest")
    uploaded_file = st.sidebar.file_uploader("Upload Manifest File", type=["txt"])

    if uploaded_file:
        try:
            # Read and process the uploaded file
            file_content = uploaded_file.read().decode("utf-8").splitlines()
            update_ship_grid(file_content, st.session_state.ship_grid, st.session_state.containers)
            st.session_state.initial_plot = plotly_visualize_grid(
                st.session_state.ship_grid, title="Initial Ship Grid"
            )
            st.success("Ship grid updated successfully from manifest.")
        except Exception as e:
            st.error(f"Error reading the file: {e}")

    # Display initial grid
    if st.session_state.initial_plot:
        st.subheader("Initial Ship Grid")
        st.plotly_chart(st.session_state.initial_plot)

    # Perform balancing
    if st.button("Balance Ship"):
        left_balance, right_balance, balanced = calculate_balance(st.session_state.ship_grid)
        if balanced:
            st.success("The ship is already balanced!")
        else:
            steps, ship_grids, status = balance(st.session_state.ship_grid, st.session_state.containers)
            st.session_state.steps = steps  # Save balancing steps
            st.session_state.ship_grid = ship_grids[-1]  # Update grid to final balanced state
            st.session_state.final_plot = plotly_visualize_grid(
                st.session_state.ship_grid, title="Final Ship Grid After Balancing"
            )
            if status:
                st.success("Ship balanced successfully!")
            else:
                st.warning("Ship could not be perfectly balanced. Check balancing steps.")

    # Display balancing steps
    if st.session_state.steps:
        st.subheader("Balancing Steps")
        for step_number, step_list in enumerate(st.session_state.steps):
            st.markdown(f"**Step {step_number + 1}:**")
            for sub_step_number, sub_step in enumerate(step_list):
                st.write(f"{sub_step_number + 1}. {sub_step}")

    # Display final grid after balancing
    if st.session_state.final_plot:
        st.subheader("Final Ship Grid After Balancing")
        st.plotly_chart(st.session_state.final_plot)

    
    # st.title("Ship Balancing")

    # # Ensure ship grid and containers are initialized
    # if "ship_grid" not in st.session_state or "containers" not in st.session_state:
    #     st.error("No manifest loaded. Please upload a manifest in the File Handler page.")
    #     return

    # # Display current balance
    # left_balance, right_balance, balanced = calculate_balance(st.session_state.ship_grid)
    # st.write(f"Total Weight: {left_balance + right_balance}")
    # st.write(f"Left Balance: {left_balance}")
    # st.write(f"Right Balance: {right_balance}")

    # # Initialize steps if not already done
    # if "balancing_steps" not in st.session_state:
    #     st.session_state["balancing_steps"] = []
    #     st.session_state["grid_states"] = []
    #     st.session_state["current_step"] = 0

    # # If not already balanced, calculate balancing steps
    # if not st.session_state["balancing_steps"] and st.button("Balance Ship"):
    #     steps, ship_grids, status = balance(st.session_state.ship_grid, st.session_state.containers)
    #     st.session_state["balancing_steps"] = steps
    #     st.session_state["grid_states"] = [convert_to_display_grid(grid) for grid in ship_grids]
    #     st.session_state["current_step"] = 0

    #     if status:
    #         st.success("Ship successfully balanced!")
    #     else:
    #         st.warning("Balancing completed with SIFT protocol.")

    # # Step-by-step operations
    # if "balancing_steps" in st.session_state and st.session_state["balancing_steps"]:
    #     st.subheader("Step-by-Step Balancing Operation")
    #     current_step = st.session_state["current_step"]
    #     steps = st.session_state["balancing_steps"]
    #     grid_states = st.session_state["grid_states"]

    #     if current_step < len(steps):
    #         # Display the current step description and grid state
    #         st.write(f"Step {current_step + 1}: {steps[current_step]}")
    #         display_grid(grid_states[current_step], title=f"Step {current_step + 1}")

    #         # Navigation buttons
    #         col1, col2 = st.columns(2)
    #         with col1:
    #             if current_step > 0 and st.button("Previous Step"):
    #                 st.session_state["current_step"] -= 1
    #                 st.rerun()
    #         with col2:
    #             if current_step < len(steps) - 1 and st.button("Next Step"):
    #                 st.session_state["current_step"] += 1
    #                 st.rerun()
    #     else:
    #         st.success("Balancing process completed!")
    #         if st.button("Finish"):
    #             st.session_state.pop("balancing_steps")
    #             st.session_state.pop("grid_states")
    #             st.session_state["current_step"] = 0
    #             st.rerun()



'''

import streamlit as st
import plotly.graph_objects as go
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
                [0.5, "lightgray"], # NAN slots
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


def balancing_page():
    # Streamlit App
    st.title("Ship Balancing Project")

    # Sidebar for grid setup
    st.sidebar.header("Ship Grid Setup")
    rows = 8  # Fixed to match the manifest
    columns = 12  # Fixed to match the manifest
    
    if "steps" not in st.session_state:
        st.session_state["steps"] = []
        
    if "final_plot" not in st.session_state:
        st.session_state.final_plot = None

    # Initialize session state
    if "ship_grid" not in st.session_state:
        st.session_state.ship_grid = create_ship_grid(rows, columns)
        st.session_state.containers = []
        st.session_state.initial_plot = None
        st.session_state.final_plot = None
        st.session_state.steps = []

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
        left_balance, right_balance, balanced = calculate_balance(st.session_state.ship_grid)
        if balanced:
            st.success("The ship is already balanced!")
        else:
            steps, ship_grids, status = balance(st.session_state.ship_grid, st.session_state.containers)
            st.session_state.steps = steps
            st.session_state.ship_grid = ship_grids[-1]
            st.session_state.final_plot = plotly_visualize_grid(
                st.session_state.ship_grid, title="Final Ship Grid After Balancing"
            )
            if status:
                st.success("Ship balanced successfully!")
            else:
                st.warning("Ship could not be perfectly balanced. Check balancing steps.")

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

'''
import streamlit as st
import plotly.graph_objects as go
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


def balancing_page():
    # Streamlit App
    st.title("Ship Balancing Project")

    # Sidebar for grid setup
    st.sidebar.header("Ship Grid Setup")
    rows = 8  # Fixed to match the manifest
    columns = 12  # Fixed to match the manifest
    
    if "steps" not in st.session_state:
        st.session_state["steps"] = []
        
    if "final_plot" not in st.session_state:
        st.session_state.final_plot = None

    # Initialize session state
    if "ship_grid" not in st.session_state:
        st.session_state.ship_grid = create_ship_grid(rows, columns)
        st.session_state.containers = []
        st.session_state.initial_plot = None
        st.session_state.final_plot = None
        st.session_state.steps = []

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
        left_balance, right_balance, balanced = calculate_balance(st.session_state.ship_grid)
        if balanced:
            st.success("The ship is already balanced!")
        else:
            steps, ship_grids, status = balance(st.session_state.ship_grid, st.session_state.containers)
            st.session_state.steps = steps
            st.session_state.ship_grid = ship_grids[-1]
            st.session_state.final_plot = plotly_visualize_grid(
                st.session_state.ship_grid, title="Final Ship Grid After Balancing"
            )
            if status:
                st.success("Ship balanced successfully!")
            else:
                st.warning("Ship could not be perfectly balanced. Check balancing steps.")

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


'''


import streamlit as st
import plotly.graph_objects as go
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

def visualize_steps_with_grids():
    """
    Displays balancing steps along with dynamic grid visualizations for each sub-step.
    """
    if "steps" in st.session_state and "ship_grids" in st.session_state:
        st.subheader("Balancing Steps and Grids")

        # Select Step
        total_steps = len(st.session_state.steps)
        step_number = st.number_input("Select Step", min_value=1, max_value=total_steps, value=1, step=1) - 1

        # Display sub-steps for the selected step
        selected_step = st.session_state.steps[step_number]
        step_grids = st.session_state.ship_grids[step_number]
        total_sub_steps = len(selected_step)

        sub_step_number = st.number_input(
            "Select Sub-Step", min_value=1, max_value=total_sub_steps, value=1, step=1
        ) - 1

        # Get current sub-step details
        current_sub_step = selected_step[sub_step_number]
        from_coords, to_coords = current_sub_step.replace("[", "").replace("]", "").split(" to ")
        from_x, from_y = map(int, from_coords.split(","))
        to_x, to_y = map(int, to_coords.split(","))

        # Visualize the grid for the current sub-step with highlights
        def visualize_sub_step(grid, from_coords, to_coords):
            """
            Visualize the grid for the current sub-step with highlights for source and destination.
            Includes annotations for container names or status, including the moved container.
            """
            z = []  # Color mapping for grid cells
            annotations = []  # Annotations for text inside cells
            moved_container_name = None  # To track the container being moved

            for row_idx, row in enumerate(grid):
                z_row = []
                for col_idx, slot in enumerate(row):
                    if (row_idx, col_idx) == (from_coords[0], from_coords[1]):
                        # Highlight source in red
                        z_row.append(2)
                        moved_container_name = slot.container.name if slot.container else ""
                    elif (row_idx, col_idx) == (to_coords[0], to_coords[1]):
                        # Highlight destination in green
                        z_row.append(3)
                    elif slot.container:
                        # Occupied (blue)
                        z_row.append(1)
                    elif not slot.available:
                        # NAN (light gray)
                        z_row.append(-1)
                    else:
                        # UNUSED (white)
                        z_row.append(0)

                    # Add annotation text for this cell
                    if slot.container:
                        text = slot.container.name  # Container name
                        color = "white"
                    elif (row_idx, col_idx) == (from_coords[0], from_coords[1]):
                        text = moved_container_name  # Show the moved container at source
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

            # Add annotations to the plot
            fig.update_layout(
                title=dict(text="Current Sub-Step Grid Visualization", x=0.5),
                xaxis=dict(
                    title="Columns",
                    tickvals=[i for i in range(len(grid[0]))],
                    ticktext=[f"{i + 1:02}" for i in range(len(grid[0]))],
                ),
                yaxis=dict(
                    title="Rows",
                    tickvals=[i for i in range(len(grid))],
                    ticktext=[f"{i + 1:02}" for i in range(len(grid))],
                ),
                annotations=annotations,
                plot_bgcolor="white",
            )
            return fig



        # Display the grid for the current sub-step
        grid_plot = visualize_sub_step(step_grids, (from_x, from_y), (to_x, to_y))
        st.plotly_chart(grid_plot)

        # Display details of the current sub-step
        st.markdown(f"### Sub-Step Details")
        st.write(f"**Container Movement:** {current_sub_step}")
        st.write(f"**From Coordinates:** [{from_x + 1},{from_y + 1}]")
        st.write(f"**To Coordinates:** [{to_x + 1},{to_y + 1}]")



def balancing_page():
    # Streamlit App
    st.title("Ship Balancing Project")

    # Sidebar for grid setup
    st.sidebar.header("Ship Grid Setup")
    rows = 8  # Fixed to match the manifest
    columns = 12  # Fixed to match the manifest

    if "steps" not in st.session_state:
        st.session_state["steps"] = []
        
    if "ship_grids" not in st.session_state:  # Ensure ship_grids is initialized
        st.session_state["ship_grids"] = []

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
        ["Steps", "Steps with Grids", "Tab 3 Placeholder"],
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
        visualize_steps_with_grids()


    elif selected_tab == "Tab 3 Placeholder":
        # Placeholder for future content
        st.subheader("Tab 3 Placeholder")
        st.write("Content for this tab will be implemented soon!")

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
