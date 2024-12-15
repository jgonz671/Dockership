import streamlit as st
from utils.components.buttons import create_navigation_button, create_logout_button
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

    # Create a container for the buttons
    st.markdown("<style>div.row-widget.stButton > button { width: 100%; height: 50px; }</style>", unsafe_allow_html=True)

    # Main button layout
    button_container = st.container()
    with button_container:
        # First row: Operation buttons
        col1, col2 = st.columns([1, 1], gap="large")  # Three equally spaced columns
        with col1:
            if st.button("Loading/Unloading Operation"):
                next_page = perform_operation(username, "loading")
                state_manager.set_page(next_page)
                st.rerun()
        with col2:
            if st.button("Balancing Operation"):
                next_page = perform_operation(username, "balancing")
                state_manager.set_page(next_page)
                st.rerun()

        # Second row: Footer buttons (Upload and Logout)
        st.markdown("<br>", unsafe_allow_html=True)  # Add spacing between rows
        col3, col4 = st.columns([1, 1], gap="large")  # Two equally spaced columns for footer buttons
        with col3:
            if create_navigation_button(
                label="Upload Another File",
                page_name="file_handler",
                session_state=st.session_state
            ):
                if "file_content" in st.session_state:
                    del st.session_state.file_content
                st.rerun()  # Navigate to the File Handler page
        with col4:
            create_logout_button(st.session_state)