# Dockership/pages/file_handler/file_handler.py

import streamlit as st
from utils.file_handler import process_file, log_file_upload, log_proceed_to_operations
from utils.validators import validate_file_content
from utils.components.buttons import create_button, create_navigation_button, create_logout_button
from config.db_config import DBConfig

# Initialize DBConfig
db_config = DBConfig()
db = db_config.connect()
logs_collection = db_config.get_collection("logs")


def file_handler():
    """
    Frontend for the File Handler page. Allows users to upload a file, processes it,
    and displays feedback. Logs actions such as file uploads and proceeding to operations.
    """
    st.title("File Handler")
    username = st.session_state.get("user_name", "Guest")
    first_name = st.session_state.get("first_name", "User")
    st.write(f"Hello, {first_name}!")

    # File uploader
    uploaded_file = st.file_uploader(
        "Upload a .txt file to proceed:", type=["txt"])

    if uploaded_file:
        # Extract and display file content
        file_content = uploaded_file.read().decode("utf-8")
        filename = uploaded_file.name
        st.write("Uploaded File Content:")
        st.text(file_content)

        # Log file upload
        log_file_upload(logs_collection, username, filename)

        # Validate file content
        is_valid, error_message = validate_file_content(file_content)
        if not is_valid:
            st.error(error_message)
            return

        # Process the file
        processed_data = process_file(file_content)

        # Display processed data
        st.success("File processed successfully!")
        st.write(f"Total lines in file: {processed_data['line_count']}")
        st.write("First 10 lines of the file:")
        st.text("\n".join(processed_data["first_10_lines"]))

        # Store processed content in session state
        st.session_state.file_content = file_content

        # Proceed to operations
        if create_button("Proceed to Operations"):
            log_proceed_to_operations(logs_collection, username)
            st.session_state["page"] = "operation"  # Update page to "operation"
            st.rerun()  # Trigger rerun to navigate to the new page

    # Logout button 
    create_logout_button(st.session_state)
