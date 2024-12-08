import streamlit as st
from utils.components.buttons import create_button
from tasks.operation import perform_operation
from utils.state_manager import StateManager

def operation():
    """
    Operations page for selecting a task to perform.
    """
    # Get session state and user information
    state_manager = StateManager(st.session_state)
    username = st.session_state.get("user_name", "Guest")
    first_name = st.session_state.get("first_name", "User")

    # Welcome text
    st.title("Operations")
    st.subheader(f"Welcome, {first_name}!")
    st.write("What operation would you like to perform?")

    # Buttons for operations
    col1, col2 = st.columns(2)
    with col1:
        if create_button("Loading/Unloading Operation"):
            # Perform loading/unloading operation
            next_page = perform_operation(username, "loading")
            state_manager.set_page(next_page)
            st.rerun()  # Immediately navigate to the next page

    with col2:
        if create_button("Balancing Operation"):
            # Perform balancing operation
            next_page = perform_operation(username, "balancing")
            state_manager.set_page(next_page)
            st.rerun()  # Immediately navigate to the next page
