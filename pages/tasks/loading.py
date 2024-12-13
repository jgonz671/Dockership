import streamlit as st
# Import utility functions
from utils.grid_utils import plotly_visualize_grid, validate_ship_grid
from tasks.loading import optimize_load_unload
from utils.state_manager import StateManager
from utils.components.buttons import create_navigation_button


def loading_task():
    """
    UI for managing loading and unloading tasks.
    """
    # Create a container for the back button and place it at the top-left corner
    top_left = st.container()
    with top_left:
        # Create two columns: one narrow (for the button) and one wide
        col1, col2 = st.columns([1, 9])
        with col1:
            create_navigation_button(
                label="<-- Back",
                page_name="operation",
                session_state=st.session_state
            )

    st.title("Loading/Unloading Task")

    # Ensure a ship grid is available
    if "updated_grid" in st.session_state and st.session_state["updated_grid"]:
        st.session_state["ship_grid"] = st.session_state["updated_grid"]
    elif "ship_grid" not in st.session_state or not st.session_state["ship_grid"]:
        st.error(
            "No manifest loaded. Please upload a manifest in the File Handler page."
        )
        return

    # Validate the grid structure using grid_utils
    try:
        grid = st.session_state["ship_grid"]
        validate_ship_grid(grid)  # Ensures the grid is structured as expected
    except ValueError as e:
        st.error(f"Grid validation failed: {e}")
        return

    # Display available container names for reference
    container_names = [
        slot.container.name
        for row in st.session_state["ship_grid"]
        for slot in row if slot.container
    ]
    if container_names:
        st.write("### Available Containers")
        st.write(", ".join(container_names))
    else:
        st.warning("No containers available in the manifest.")

    # Display the current grid using plotly_visualize_grid from grid_utils
    st.plotly_chart(plotly_visualize_grid(
        st.session_state["ship_grid"], title="Current Ship Layout"
    ))

    # Input for loading/unloading operations
    st.subheader("Enter Loading/Unloading Instructions")
    loading_input = st.text_area("Containers to Load (comma-separated):")
    unloading_input = st.text_area("Containers to Unload (comma-separated):")

    if st.button("Calculate Optimal Operations"):
        loading_list = [item.strip()
                        for item in loading_input.split(",") if item.strip()]
        unloading_list = [item.strip()
                          for item in unloading_input.split(",") if item.strip()]

        # Check if input is valid
        if not loading_list and not unloading_list:
            st.warning(
                "Please provide at least one container to load or unload."
            )
            return

        # Log inputs for debugging
        st.write("### Debug Information")
        st.write("Containers to Load:", loading_list)
        st.write("Containers to Unload:", unloading_list)

        # Calculate operations
        try:
            operations, grid_states = optimize_load_unload(
                st.session_state["ship_grid"], unloading_list, loading_list
            )
            if not operations:
                st.warning(
                    "No valid operations found. Ensure container names match those in the manifest."
                )
            else:
                st.session_state["operations"] = operations
                st.session_state["grid_states"] = grid_states
                st.session_state["current_step"] = 0
                # Save updated grid
                st.session_state["updated_grid"] = grid_states[-1]
                st.success(
                    "Optimal operations calculated! Use the navigation buttons below to proceed."
                )
        except Exception as e:
            st.error(f"Error calculating operations: {e}")

    # Step-by-step operations
    if "operations" in st.session_state and st.session_state["operations"]:
        st.subheader("Step-by-Step Operation")
        current_step = st.session_state["current_step"]
        operations = st.session_state["operations"]
        grid_states = st.session_state["grid_states"]

        if current_step < len(operations):
            st.write(
                f"Step {current_step + 1}: {operations[current_step]['description']}"
            )
            st.plotly_chart(plotly_visualize_grid(
                grid_states[current_step], title=f"Step {current_step + 1}"
            ))

            # Navigation buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Next Step"):
                    st.session_state["current_step"] += 1
                    st.rerun()
            with col2:
                if current_step > 0 and st.button("Previous Step"):
                    st.session_state["current_step"] -= 1
                    st.rerun()
        else:
            st.success("All operations completed!")
            if st.button("Finish"):
                st.session_state.pop("operations")
                st.session_state.pop("grid_states")
                st.session_state["current_step"] = 0
                st.rerun()
