import streamlit as st
from utils.file_handler import process_file_content, log_file_upload, log_proceed_to_operations
from utils.validators import validate_file_content
from utils.components.buttons import create_button, create_logout_button
from utils.grid_utils import create_ship_grid, validate_ship_grid
from tasks.ship_balancer import update_ship_grid
from config.db_config import DBConfig

# Initialize DBConfig
db_config = DBConfig()
db = db_config.connect()
logs_collection = db_config.get_collection("logs")


def file_handler():
    """
    Frontend for the File Handler page. Allows users to upload a file, process it,
    and store content for loading/unloading tasks.
    """
    st.title("File Handler")
    username = st.session_state.get("username", "User")
    first_name = st.session_state.get("firstname", "User")
    st.write(f"Hello, {first_name}!")

    # File uploader
    uploaded_file = st.file_uploader(
        "Upload a .txt file to proceed:", type=["txt"])

    if uploaded_file:
        # Read file content
        file_content = uploaded_file.read().decode("utf-8")
        filename = uploaded_file.name

        # Log file upload
        log_file_upload(logs_collection, username, filename)

        # Validate file content
        is_valid, error_message = validate_file_content(file_content)
        if not is_valid:
            st.error(error_message)
            return

        # Process file and initialize grid
        file_lines = process_file_content(file_content)
        st.session_state.file_content = file_content  # Store raw manifest
        st.session_state.filename = filename  # Store the file name
        if "ship_grid" not in st.session_state:
            st.session_state.ship_grid = create_ship_grid(
                8, 12)  # Initialize empty grid
        st.session_state.containers = []  # Initialize container list
        update_ship_grid(
            file_lines, st.session_state.ship_grid, st.session_state.containers)

        # Validate grid structure
        try:
            validate_ship_grid(st.session_state.ship_grid)
        except ValueError as e:
            st.error(f"Grid validation failed: {e}")
            return

        # Display processed data
        st.success("File processed successfully!")
        st.write(f"File Name: {filename}")
        st.write(f"Total Lines in File: {len(file_lines)}")
        st.write("Preview of Uploaded File:")
        st.text("\n".join(file_lines[:10]))  # Show first 10 lines

        # Provide navigation to the next page
        if create_button("Proceed to Operations"):
            log_proceed_to_operations(logs_collection, username)
            st.session_state.page = "operation"
            st.rerun()

    # Logout button
    create_logout_button(st.session_state)
