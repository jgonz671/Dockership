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
                st.write(f"{sub_step_number + 1}. {sub_step}")

    # Display final grid after balancing
    if st.session_state.final_plot:
        st.subheader("Final Ship Grid After Balancing")
        st.plotly_chart(st.session_state.final_plot)
