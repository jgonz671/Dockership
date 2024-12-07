# Dockership/pages/auth/login.py
import streamlit as st
from utils.components.buttons import create_button, create_navigation_button
from utils.components.textboxes import create_textbox
from utils.validators import validate_username
from auth.login import check_user_exists, log_user_action

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
            # Validate username
            is_valid, error_message = validate_username(username)
            if not is_valid:
                st.error(error_message)
                return

            # Check if user exists
            user = check_user_exists(username)
            if user:
                st.session_state["user_name"] = user["username"]
                st.session_state["first_name"] = user["first_name"]
                st.session_state["page"] = "file_handler"  # Redirect to file handler
                log_user_action(username, "Login successful")  # Log the action

                st.rerun()
            else:
                st.error("Username not found. Please register.")

    with col2:
        # Navigation button for registration
        create_navigation_button("Need an account? Register here", "register", st.session_state)
