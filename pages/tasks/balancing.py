import streamlit as st
from utils.components.buttons import create_navigation_button
from utils.grid_utils import create_ship_grid, validate_ship_grid, plotly_visualize_grid
from tasks.ship_balancer import update_ship_grid, calculate_balance, balance


def balancing_page():
    """
    Streamlit page for managing ship balancing tasks.
    """
    # Create a container for the back button and place it at the top-left corner
    top_left = st.container()
    with top_left:
        col1, col2 = st.columns([1, 9])
        with col1:
            create_navigation_button(
                label="<-- Back",
                page_name="operation",
                session_state=st.session_state
            )

    st.title("Ship Balancing Project")

    # Ensure a ship grid is available
    if "updated_grid" in st.session_state and st.session_state["updated_grid"]:
        st.session_state["ship_grid"] = st.session_state["updated_grid"]
    elif "ship_grid" not in st.session_state or not st.session_state["ship_grid"]:
        st.error(
            "No manifest loaded. Please upload a manifest in the File Handler page.")
        return

    # Validate the grid structure
    try:
        validate_ship_grid(st.session_state["ship_grid"])
    except ValueError as e:
        st.error(f"Grid validation failed: {e}")
        return

    # Display the current grid
    st.plotly_chart(plotly_visualize_grid(
        st.session_state["ship_grid"], title="Current Ship Layout"))

    # Perform balancing
    if st.button("Balance Ship"):
        left_balance, right_balance, balanced = calculate_balance(
            st.session_state["ship_grid"])
        if balanced:
            st.success("The ship is already balanced!")
        else:
            try:
                steps, ship_grids, status = balance(
                    st.session_state["ship_grid"], st.session_state.get("containers", []))
                st.session_state["steps"] = steps
                # Save updated grid
                st.session_state["updated_grid"] = ship_grids[-1]
                st.session_state["final_plot"] = plotly_visualize_grid(
                    st.session_state["updated_grid"], title="Final Ship Grid After Balancing"
                )
                if status:
                    st.success("Ship balanced successfully!")
                else:
                    st.warning(
                        "Ship could not be perfectly balanced. Check balancing steps.")
            except Exception as e:
                st.error(f"An error occurred during balancing: {e}")

    # Display balancing steps
    if st.session_state.get("steps"):
        st.subheader("Balancing Steps")
        for step_number, step_list in enumerate(st.session_state["steps"]):
            st.markdown(f"**Step {step_number + 1}:**")
            for sub_step_number, sub_step in enumerate(step_list):
                st.write(f"{sub_step_number + 1}. {sub_step}")

    # Display final grid after balancing
    if st.session_state.get("final_plot"):
        st.subheader("Final Ship Grid After Balancing")
        st.plotly_chart(st.session_state["final_plot"])
