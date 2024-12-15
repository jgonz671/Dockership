import streamlit as st

from utils.components.buttons import create_button, create_navigation_button
from utils.components.textboxes import create_textbox
from auth.login import validate_and_check_user


def login():
    """
    Login page for users. Validates username, checks database for existence, and saves user data to session state.
    """
    st.title("Dockership Login")
    st.write("Please enter your username to log in:")

    username = create_textbox("Username:")

    col1, col2 = st.columns([1, 1])
    with col1:
        if create_button("Login"):
            # Call the backend function to validate and check the user
            success, error_message, user = validate_and_check_user(username)

            if not success:
                # Display error messages
                try:
                    st.toast(error_message, icon="❌")
                except AttributeError:
                    st.error(error_message)
                return

            # Save user details to session state
            st.session_state.username = user["username"]
            st.session_state.firstname = user["first_name"]
            st.session_state.page = "file_handler"  # Redirect to file handler

            # Display success message
            try:
                st.toast(f"Welcome, {user['first_name']}!", icon="✅")
            except AttributeError:
                st.success(f"Welcome, {user['first_name']}!")

            # Trigger rerun to load the next page
            st.rerun()

    with col2:
        # Navigation button for registration page
        create_navigation_button(
            "Need an account? Register here", "register", st.session_state
        )
