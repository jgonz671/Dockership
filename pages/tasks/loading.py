import streamlit as st
from utils.visualizer import display_grid
from tasks.loading import optimize_load_unload
from utils.state_manager import StateManager


def loading_task():
    """
    UI for managing loading and unloading tasks.
    """
    st.title("Loading/Unloading Task")

    # Debugging output
    st.write("Debugging session state in Loading page:")
    st.write(st.session_state)

    # Ensure the ship grid is initialized
    if "ship_grid" not in st.session_state:
        st.error("No manifest loaded. Please upload a manifest in the File Handler page.")
        return

    # State manager for navigation
    state_manager = StateManager(st.session_state)

    # Display the current grid layout
    ship_grid = st.session_state["ship_grid"]
    display_grid(ship_grid, title="Current Ship Layout")

    # Input for loading/unloading operations
    st.subheader("Enter Loading/Unloading Instructions")
    loading_input = st.text_area("Containers to Load (comma-separated):", "")
    unloading_input = st.text_area("Containers to Unload (comma-separated):", "")

    # State to keep track of steps
    if "operations" not in st.session_state:
        st.session_state["operations"] = []

    # Calculate optimal operations
    if st.button("Calculate Optimal Operations"):
        load_list = [item.strip() for item in loading_input.split(",") if item.strip()]
        unload_list = [item.strip() for item in unloading_input.split(",") if item.strip()]

        if not load_list and not unload_list:
            st.warning("Please provide at least one container to load or unload.")
            return

        # Perform operations
        operations, _ = optimize_load_unload(ship_grid, unload_list, load_list)
        st.session_state["operations"] = operations
        st.session_state["current_step"] = 0
        st.success("Optimal operations calculated! Use the navigation buttons below to proceed.")

    # Step navigation for operations
    if st.session_state["operations"]:
        st.subheader("Step-by-Step Operation")
        current_step = st.session_state.get("current_step", 0)
        operations = st.session_state["operations"]

        if current_step < len(operations):
            operation = operations[current_step]
            action = operation["action"]
            description = operation["description"]
            grid = operation["grid"]

            st.write(f"Step {current_step + 1}: {description}")
            display_grid(grid, title=f"Grid After Step {current_step + 1}")

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
                st.session_state["operations"] = []
                st.session_state["current_step"] = 0
                st.rerun()
