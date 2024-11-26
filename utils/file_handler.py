import streamlit as st
from utils.visualizer import parse_input, display_grid


def file_handler():
    st.title("File Handler")
    st.write(f"Hello, {st.session_state.user_name}!")
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