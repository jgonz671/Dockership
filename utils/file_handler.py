import streamlit as st
from utils.visualizer import parse_input, display_grid


def file_handler():
    st.title("File Handler")
    st.write(f"Hello, {st.session_state.first_name}!")
    st.write("Upload a .txt file to proceed:")

    uploaded_file = st.file_uploader("Choose a .txt file", type=["txt"])

    if uploaded_file is not None:
        file_content = uploaded_file.read().decode("utf-8")
        st.write("File content:")
        st.text(file_content)

        # Store file content in session state
        st.session_state.file_content = file_content

        # Perform any processing you need with the file content
        st.success("File processed successfully!")
        if st.button("Proceed to Operations"):
            return True

    return False
# work on making the webpage reload immedaitely when i make changes to the code.
# Make a logout button for all pages other than the login page and the register page.
# Adjust the register and login buttons on login and register pages.
# Fix the issue where i have to press the buttons twice to get the desired effect.