import streamlit as st
from utils.components.buttons import create_button, create_navigation_button
from utils.grid_utils import plotly_visualize_grid
from tasks.operation import perform_operation
from utils.state_manager import StateManager


def operation():
    """
    Operations page for selecting a task to perform.
    Displays the current ship grid and allows users to select an operation.
    """
    # Get session state and user information
    state_manager = StateManager(st.session_state)
    username = st.session_state.get("user_name", "Guest")
    first_name = st.session_state.get("first_name", "User")

    # Welcome text
    st.title("Operations")
    st.subheader(f"Welcome, {first_name}!")
    st.write("Current Ship Grid:")

    # Display the current ship grid
    if "ship_grid" in st.session_state:
        st.plotly_chart(plotly_visualize_grid(
            st.session_state["ship_grid"], title="Current Ship Layout"
        ))
    else:
        st.error(
            "No grid data available. Please upload a file in the File Handler page.")
        return

    # Centered buttons for operations
    col1, col2, col3 = st.columns([1, 2, 1])  # Equal spacing on the sides
    with col2:
        col_a, col_b = st.columns(2, gap="large")  # Two buttons equidistant
        with col_a:
            if create_button("Loading/Unloading Operation"):
                next_page = perform_operation(username, "loading")
                state_manager.set_page(next_page)
                st.rerun()

        with col_b:
            if create_button("Balancing Operation"):
                next_page = perform_operation(username, "balancing")
                state_manager.set_page(next_page)
                st.rerun()

    # Bottom-left button for uploading another file
    bottom_left = st.container()
    with bottom_left:
        col1, _ = st.columns([1, 9])  # Position bottom-left button
        with col1:
            if create_navigation_button(
                label="Upload Another File",
                page_name="file_handler",
                session_state=st.session_state
            ):
                # Clear the current file from session state
                st.session_state.pop("file_content", None)
                st.session_state.pop("ship_grid", None)
                st.rerun()
