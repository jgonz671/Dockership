import os
import streamlit as st
import plotly.graph_objects as go
from copy import deepcopy
from utils.components.buttons import create_navigation_button
from utils.logging import log_action
from tasks.ship_balancer import (
    create_ship_grid,
    update_ship_grid,
    Container,
    Slot,
    calculate_balance,
    balance,
)

from tasks.balancing_utils import (
    plotly_visualize_grid,
    convert_grid_to_manifest,
    append_outbound_to_filename,
    plotly_visualize_grid_with_overlay,
    generate_animation_with_annotations,
    generate_stepwise_animation
)
from utils.components.buttons import create_navigation_button, create_text_input_with_logging


def visualize_steps_with_overlay():
    """
    Visualize the base grid for the selected step and overlay it with sub-step movements.
    """
    if "steps" in st.session_state and "ship_grids" in st.session_state:
        st.subheader("Container Movement Details")
        # Ensure the initial grid is set once

        st.markdown("""
        Select a **Container (Step)** to view the corresponding container.  
        Then, select a **Movement (Sub-Step)** to visualize the movement of the selected container within the ship grid.
        Blocks `Red` represent the container's current position.
        Blocks `Green` represent the container's next position.
        
        """)

        if "initial_grid" not in st.session_state:
            # Make a deep copy of the initial grid to ensure it's not inadvertently modified
            st.session_state.initial_grid = [row[:]
                                             for row in st.session_state.ship_grid]
        # Select Step
        total_steps = len(st.session_state.steps)
        step_number = st.number_input(
            "Select Container (Step)", min_value=1, max_value=total_steps, value=1, step=1) - 1
        # Base grid for the selected step
        base_grid = (
            st.session_state.initial_grid
            if step_number == 0
            else st.session_state.ship_grids[step_number - 1]
        )
        # base_grid_plot = plotly_visualize_grid(base_grid, title=f"Base Grid for Step {step_number + 1}")
        # Display base grid
        # st.plotly_chart(base_grid_plot, use_container_width=True)
        # Select Sub-Step
        selected_step = st.session_state.steps[step_number]
        total_sub_steps = len(selected_step)
        sub_step_number = st.number_input(
            "Select Movement (Sub-Step)", min_value=1, max_value=total_sub_steps, value=1, step=1
        ) - 1
        # Get current sub-step details
        current_sub_step = selected_step[sub_step_number]
        from_coords, to_coords = current_sub_step.replace("[", "").replace("]", "").split(" to ")
        from_x, from_y = map(int, from_coords.split(","))
        to_x, to_y = map(int, to_coords.split(","))
        # Overlay the sub-step movement on the base grid
        overlay_plot = plotly_visualize_grid_with_overlay(
            base_grid, (from_x, from_y), (to_x,
                                          to_y), title=f"Movement for Container {step_number + 1}, Sub-Step {sub_step_number + 1}"
        )
        st.plotly_chart(overlay_plot, use_container_width=True)


def display_total_moves_and_time():
    """
    Count the total number of sub-steps and display the total moves and time taken.
    """
    # Check if steps exist in the session state
    if "steps" in st.session_state and st.session_state.steps:
        # Count the total number of sub-steps
        total_sub_steps = sum(len(step) for step in st.session_state.steps)
        total_time = total_sub_steps  # Each sub-step equals one minute

        # Display total sub-steps and time taken
        st.markdown(
            f"#### 🕒 Total Time to Balance all Containers: {total_time} minutes")
    else:
        # Show a warning if steps are not initialized or empty
        st.warning("No steps have been recorded yet.")


def balancing_page():
    col1, _ = st.columns([2, 8])  # Center the button
    with col1:
        if create_navigation_button("Back to Operations", "operation", st.session_state):
            st.rerun()
    # Streamlit App
    st.title("Ship Balancing System")
    username = st.session_state.get("username", "User")
    rows = 8  # Fixed to match the manifest
    columns = 12  # Fixed to match the manifest

    if "containers" not in st.session_state:
        st.session_state.containers = []

    if "initial_plot" not in st.session_state:
        st.session_state.initial_plot = None

    if "final_plot" not in st.session_state:
        st.session_state.final_plot = None

    if "steps" not in st.session_state:
        st.session_state.steps = []

    if "ship_grids" not in st.session_state:
        st.session_state.ship_grids = []

    # Initialize session state
    if "ship_grid" not in st.session_state:
        st.session_state.ship_grid = create_ship_grid(rows, columns)

    # Use manifest from file_handler
    elif "ship_grid" in st.session_state:
        try:
            # Use file content from file_handler
            # file_content = st.session_state.file_content.splitlines()
            # update_ship_grid(file_content, st.session_state.ship_grid, st.session_state.containers)
            st.session_state.initial_plot = plotly_visualize_grid(
                st.session_state.ship_grid, title="Initial Ship Grid"
            )
            st.success("Ship grid updated successfully from manifest.")
        except Exception as e:
            st.error(f"Error processing the manifest: {e}")
    else:
        st.error(
            "No manifest available. Please upload a file in the File Handler page.")
    # Display initial grid
    if st.session_state.initial_plot:
        st.subheader("Initial Ship Grid")
        st.plotly_chart(st.session_state.initial_plot)

    # Display current balance
    if st.button("Calculate Initial Balance"):
        left_balance, right_balance, _ = calculate_balance(
            st.session_state.ship_grid)
        st.session_state.initial_balance = (left_balance, right_balance)
        # Display metrics for current balance
        st.markdown("### 🚢 **Balance Metrics Before Balancing**")
        total_weight = left_balance + right_balance
        col1, col2, col3 = st.columns(3)  # Create columns for alignment
        with col1:
            st.metric(label="⚖️ Total Weight", value=f"{total_weight}")
        with col2:
            st.metric(label="⬅️ Left Balance", value=f"{left_balance}")
        with col3:
            st.metric(label="➡️ Right Balance", value=f"{right_balance}")

        # Insights
        st.markdown("### Insights:")
        if abs(left_balance - right_balance) == 0:
            st.success("The ship is already perfectly balanced!")
        elif abs(left_balance - right_balance) <= 5:
            st.warning(
                "The ship is slightly unbalanced but close to being balanced.")
        else:
            st.error(
                "The ship is significantly unbalanced. Balancing is highly recommended.")
    # Perform balancing
    if st.button("Balance Ship"):
        # Save the initial grid only once to preserve its state
        if "initial_grid" not in st.session_state:
            st.session_state.initial_grid = [
                row.copy() for row in st.session_state.ship_grid]
        # Calculate balance and perform balancing
        left_balance, right_balance, balanced = calculate_balance(
            st.session_state.ship_grid)
        if balanced:
            st.success("The ship is already balanced!")
        else:
            steps, ship_grids, status = balance(
                st.session_state.ship_grid, st.session_state.containers)
            st.session_state.steps = steps
            st.session_state.ship_grids = ship_grids  # Store intermediate grids
            st.session_state.ship_grid = ship_grids[-1]
            st.session_state.final_plot = plotly_visualize_grid(
                st.session_state.ship_grid, title="Final Ship Grid After Balancing"
            )
            if status:
                st.success("Ship balanced successfully!")
            else:
                st.warning("Ship could not be perfectly balanced. Using SIFT.")

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
                # Use an expander for each step to make the display compact
                with st.expander(f"Step {step_number + 1}"):
                    st.markdown(f"### Step {step_number + 1}:")
                    for sub_step_number, sub_step in enumerate(step_list):
                        # Parse and increment the coordinates
                        original_step = sub_step.replace("[", "").replace("]", "")  # Remove brackets for processing
                        from_coords, to_coords = original_step.split(" to ")  # Split into 'from' and 'to' parts
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
        # visualize_steps_with_grids()
        visualize_steps_with_overlay()

    elif selected_tab == "Block Movement Animation":
        # Animation for all steps
        generate_animation_with_annotations()

    elif selected_tab == "Steps Summary":
        if "steps" in st.session_state and "ship_grids" in st.session_state:
            st.subheader("Summarized Steps with Plots")

            def summarize_steps(steps):
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
                            # Convert to 1-based index
                            start_coords = (from_x + 1, from_y + 1)
                        # Update the latest destination
                        end_coords = (to_x + 1, to_y + 1)
                    summarized_steps.append(
                        f"[{start_coords[0]},{start_coords[1]}] to [{end_coords[0]},{end_coords[1]}]")
                return summarized_steps
            # Summarize the steps
            summarized_steps = summarize_steps(st.session_state.steps)

            for step_number, summary in enumerate(summarized_steps):
                # Use an expander for each step
                with st.expander(f"Step {step_number + 1}: {summary}"):
                    # Extract start and end coordinates
                    start_coords, end_coords = summary.split(" to ")
                    start_x, start_y = map(int, start_coords.replace(
                        "[", "").replace("]", "").split(","))
                    end_x, end_y = map(int, end_coords.replace(
                        "[", "").replace("]", "").split(","))
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
                                # Convert back to 0-based index
                                if (row_idx, col_idx) == (start[0] - 1, start[1] - 1):
                                    # Starting position (semi-transparent red)
                                    z_row.append(2)
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
                                                font=dict(
                                                    size=12, color="white"),
                                            )
                                        )
                                # Convert back to 0-based index
                                elif (row_idx, col_idx) == (end[0] - 1, end[1] - 1):
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
                                    # Empty (White)
                                    [0, "rgba(255, 255, 255, 1.0)"],
                                    # NAN (Light Gray)
                                    [0.25, "rgba(211, 211, 211, 1.0)"],
                                    # Occupied (Blue)
                                    [0.5, "rgba(0, 0, 255, 1.0)"],
                                    # Semi-Transparent Red for Start
                                    [0.75, "rgba(255, 0, 0, 0.5)"],
                                    # Green for End
                                    [1, "rgba(0, 255, 0, 1.0)"],
                                ],
                                showscale=False,
                            )
                        )
                        fig.update_layout(
                            annotations=annotations,
                            xaxis=dict(
                                tickvals=[i for i in range(len(grid[0]))],
                                ticktext=[
                                    f"{i + 1:02}" for i in range(len(grid[0]))],
                            ),
                            yaxis=dict(
                                tickvals=[i for i in range(len(grid))],
                                ticktext=[
                                    f"{i + 1:02}" for i in range(len(grid))],
                            ),
                        )
                        return fig
                    # Plot for this summarized step
                    plot = plot_grid_with_summary(
                        base_grid, (start_x, start_y), (end_x, end_y))
                    st.plotly_chart(plot, use_container_width=True)

    print("Steps in session state:", st.session_state.get(
        "steps", "No steps recorded"))
    display_total_moves_and_time()

    # Display final grid after balancing
    if st.session_state.final_plot:
        st.subheader("Final Ship Grid After Balancing")
        st.plotly_chart(st.session_state.final_plot)

        # Check if final balance metrics are already stored in session state
        if "final_balance_metrics" not in st.session_state:
            # Calculate and save the final balance metrics
            left_balance_final, right_balance_final, _ = calculate_balance(
                st.session_state.ship_grid)
            total_weight_final = left_balance_final + right_balance_final
            st.session_state.final_balance_metrics = {
                "left_balance": left_balance_final,
                "right_balance": right_balance_final,
                "total_weight": total_weight_final
            }
        else:
            # Retrieve the saved final balance metrics
            left_balance_final = st.session_state.final_balance_metrics["left_balance"]
            right_balance_final = st.session_state.final_balance_metrics["right_balance"]
            total_weight_final = st.session_state.final_balance_metrics["total_weight"]

        # Display final balance metrics
        st.markdown("### 🚢 **Balance Metrics After Balancing**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="⚖️ Total Weight", value=f"{total_weight_final}")
        with col2:
            st.metric(label="⬅️ Left Balance", value=f"{left_balance_final}")
        with col3:
            st.metric(label="➡️ Right Balance", value=f"{right_balance_final}")

    with col1:
        if st.button("Update Manifest"):
            updated_manifest = convert_grid_to_manifest(
                st.session_state.ship_grid)
            outbound_filename = append_outbound_to_filename(
                st.session_state.get("file_name", "manifest.txt")
            )
            st.session_state.updated_manifest = updated_manifest
            st.session_state.outbound_filename = outbound_filename
            st.success("Manifest updated successfully!")
            log_action(username=username, action="UPDATE_MANIFEST",
                       notes=f"{username} updated the manifest {outbound_filename}.")

    with col2:
        st.download_button(
            label="Download Updated Manifest",
            data=st.session_state.updated_manifest,
            file_name=st.session_state.outbound_filename,
            mime="text/plain",
            on_click=log_action(username=username ,action="DOWNLOAD_MANIFEST", notes=f"{username} downloaded the manifest {st.session_state.outbound_filename}.")
        )

    with col3:
        # Button for logging custom notes
        create_text_input_with_logging(username=username)
