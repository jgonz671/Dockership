import streamlit as st
from tasks.balancing import balance, calculate_balance
from utils.visualizer import display_grid

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


def balancing_page():
    st.title("Ship Balancing")

    # Ensure ship grid and containers are initialized
    if "ship_grid" not in st.session_state or "containers" not in st.session_state:
        st.error("No manifest loaded. Please upload a manifest in the File Handler page.")
        return

    # Display current balance
    left_balance, right_balance, balanced = calculate_balance(st.session_state.ship_grid)
    st.write(f"Total Weight: {left_balance + right_balance}")
    st.write(f"Left Balance: {left_balance}")
    st.write(f"Right Balance: {right_balance}")

    # Initialize steps if not already done
    if "balancing_steps" not in st.session_state:
        st.session_state["balancing_steps"] = []
        st.session_state["grid_states"] = []
        st.session_state["current_step"] = 0

    # If not already balanced, calculate balancing steps
    if not st.session_state["balancing_steps"] and st.button("Balance Ship"):
        steps, ship_grids, status = balance(st.session_state.ship_grid, st.session_state.containers)
        st.session_state["balancing_steps"] = steps
        st.session_state["grid_states"] = [convert_to_display_grid(grid) for grid in ship_grids]
        st.session_state["current_step"] = 0

        if status:
            st.success("Ship successfully balanced!")
        else:
            st.warning("Balancing completed with SIFT protocol.")

    # Step-by-step operations
    if "balancing_steps" in st.session_state and st.session_state["balancing_steps"]:
        st.subheader("Step-by-Step Balancing Operation")
        current_step = st.session_state["current_step"]
        steps = st.session_state["balancing_steps"]
        grid_states = st.session_state["grid_states"]

        if current_step < len(steps):
            # Display the current step description and grid state
            st.write(f"Step {current_step + 1}: {steps[current_step]}")
            display_grid(grid_states[current_step], title=f"Step {current_step + 1}")

            # Navigation buttons
            col1, col2 = st.columns(2)
            with col1:
                if current_step > 0 and st.button("Previous Step"):
                    st.session_state["current_step"] -= 1
                    st.rerun()
            with col2:
                if current_step < len(steps) - 1 and st.button("Next Step"):
                    st.session_state["current_step"] += 1
                    st.rerun()
        else:
            st.success("Balancing process completed!")
            if st.button("Finish"):
                st.session_state.pop("balancing_steps")
                st.session_state.pop("grid_states")
                st.session_state["current_step"] = 0
                st.rerun()
