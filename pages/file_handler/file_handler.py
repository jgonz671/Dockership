# Dockership/pages/tasks/file_handler.py

import streamlit as st
from utils.file_handler import process_file
from utils.validators import validate_file_content
from utils.components.buttons import create_button, create_navigation_button, create_logout_button

def file_handler():
    """
    Frontend for the File Handler page. Allows users to upload a file, processes it,
    and displays feedback. Also provides a logout button.
    """
    st.title("File Handler")
    st.write(f"Hello, {st.session_state.get('first_name', 'User')}!")

    # File uploader
    uploaded_file = st.file_uploader("Upload a .txt file to proceed:", type=["txt"])

    if uploaded_file:
        # Read and display file content
        file_content = uploaded_file.read().decode("utf-8")
        st.write("Uploaded File Content:")
        st.text(file_content)

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

        # Navigate to operations
        create_navigation_button("Proceed to Operations", "operation", st.session_state)

    # Logout button
    create_logout_button(st.session_state)
