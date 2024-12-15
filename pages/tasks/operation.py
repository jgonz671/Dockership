import streamlit as st
from utils.components.buttons import create_button, create_navigation_button
from tasks.operation import perform_operation
from utils.state_manager import StateManager

def operation():
    """
    Operations page for selecting a task to perform.
    """
    # Get session state and user information
    state_manager = StateManager(st.session_state)
    username = st.session_state.get("username", "User")
    first_name = st.session_state.get("firstname", "User")

    # Welcome text
    st.title("Operations")
    st.subheader(f"Welcome, {first_name}!")
    st.write("What operation would you like to perform?")

    # Centered buttons for operations
    col1, col2, col3 = st.columns([1, 2, 1])  # Equal spacing on the sides
    with col2:
        col_a, col_b = st.columns(2, gap="large")  # Two buttons equidistant
        with col_a:
            if create_button("Loading/Unloading Operation"):
                # Perform loading/unloading operation
                next_page = perform_operation(username, "loading")
                state_manager.set_page(next_page)
                st.rerun()  # Immediately navigate to the next page

        with col_b:
            if create_button("Balancing Operation"):
                # Perform balancing operation
                next_page = perform_operation(username, "balancing")
                state_manager.set_page(next_page)
                st.rerun()  # Immediately navigate to the next page

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
                if "file_content" in st.session_state:
                    del st.session_state.file_content
                st.rerun()  # Navigate to the File Handler page