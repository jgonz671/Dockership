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
    display_grid = np.empty((len(ship_grid), len(ship_grid[0])), dtype=object)

    for i, row in enumerate(ship_grid):
        for j, slot in enumerate(row):
            if slot.container:
                display_grid[i, j] = slot.container.name
            elif slot.available:
                display_grid[i, j] = "UNUSED"
            else:
                display_grid[i, j] = "NAN"

    return display_grid


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

    # Convert ship grid for display
    visual_grid = convert_to_display_grid(st.session_state.ship_grid)

    # Display initial ship grid
    display_grid(visual_grid, title="Initial Ship Layout")

    # Start balancing
    if st.button("Balance Ship"):
        steps, ship_grids, status = balance(st.session_state.ship_grid, st.session_state.containers)
        if status:
            st.success("Ship successfully balanced!")
        else:
            st.warning("Balancing completed with SIFT protocol.")

        # Display step-by-step grid updates
        for i, grid in enumerate(ship_grids):
            visual_grid = convert_to_display_grid(grid)
            st.subheader(f"Step {i + 1}")
            display_grid(visual_grid, title=f"Step {i + 1}")

        # Final balance display
        final_left, final_right, _ = calculate_balance(ship_grids[-1])
        st.write(f"Final Left Balance: {final_left}")
        st.write(f"Final Right Balance: {final_right}")
