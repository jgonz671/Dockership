import streamlit as st
from utils.visualizer import convert_to_display_grid, display_grid
from tasks.loading import optimize_load_unload
from utils.state_manager import StateManager
from utils.components.buttons import create_navigation_button

def loading_task():
    """
    UI for managing loading and unloading tasks with enhanced functionality.
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

    # Ensure ship grid is loaded
    if "ship_grid" not in st.session_state or not st.session_state["ship_grid"]:
        st.error(
            "No manifest loaded. Please upload a manifest in the File Handler page.")
        return

    # Display available container names and weights for reference
    container_info = [
        (slot.container.name, slot.container.weight)
        for row in st.session_state["ship_grid"]
        for slot in row if slot.has_container
    ]
    if container_info:
        st.write("### Available Containers")
        st.write(", ".join([f"{name} (Weight: {weight})" for name, weight in container_info]))
    else:
        st.warning("No containers available in the manifest.")

    # Display the current grid with weights
    visual_grid = convert_to_display_grid(st.session_state["ship_grid"], include_weights=True)
    display_grid(visual_grid, title="Current Ship Layout")

    # Input for loading/unloading operations
    st.subheader("Enter Loading/Unloading Instructions")
    st.text("Example Input: Container1:100, Container2:150")
    loading_input = st.text_area("Containers to Load (comma-separated):")
    unloading_input = st.text_area("Containers to Unload (comma-separated):")

    if st.button("Calculate Optimal Operations"):
        # Parse loading input
        try:
            loading_list = [
                {
                    "name": item.split(":")[0].strip(),
                    "weight": float(item.split(":")[1].strip())
                } for item in loading_input.split(",") if item.strip()
            ]
        except (IndexError, ValueError):
            st.warning("Invalid format for loading input. Use format: Name:Weight")
            return

        unloading_list = [item.strip() for item in unloading_input.split(",") if item.strip()]

        # Check if input is valid
        if not loading_list and not unloading_list:
            st.warning("Please provide at least one container to load or unload.")
            return

        # Log inputs for debugging
        st.write("### Debug Information")
        st.write("Containers to Load:", loading_list)
        st.write("Containers to Unload:", unloading_list)

        # Calculate operations
        operations, grid_states = optimize_load_unload(
            st.session_state["ship_grid"], unloading_list, loading_list
        )
        if not operations:
            st.warning(
                "No valid operations found. Ensure container names match those in the manifest and unloading follows stacking rules.")
        else:
            st.session_state["operations"] = operations
            st.session_state["grid_states"] = grid_states
            st.session_state["current_step"] = 0
            st.success(
                "Optimal operations calculated! Use the navigation buttons below to proceed.")

    # Step-by-step operations
    if "operations" in st.session_state and st.session_state["operations"]:
        st.subheader("Step-by-Step Operation")
        current_step = st.session_state["current_step"]
        operations = st.session_state["operations"]
        grid_states = st.session_state["grid_states"]

        if current_step < len(operations):
            st.write(
                f"Step {current_step + 1}: {operations[current_step]['description']}")
            display_grid(grid_states[current_step],
                         title=f"Step {current_step + 1}")

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
