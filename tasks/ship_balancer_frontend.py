import streamlit as st
import plotly.graph_objects as go
from ship_balancer import (
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

# Streamlit App
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
