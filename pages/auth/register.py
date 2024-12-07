import streamlit as st

from utils.components.buttons import create_button, create_navigation_button
from utils.components.textboxes import create_textbox
from utils.validators import validate_username, validate_name
from auth.register import register_user
from config.db_config import DBConfig
from utils.logging import log_user_action

# Initialize DBConfig
db_config = DBConfig()
db = db_config.connect()
logs_collection = db_config.get_collection("logs")


def register():
    """
    Registration page where a new user can create their account. Checks for unique username and valid name format.
    """
    st.title("User Registration")

    first_name = create_textbox("First Name (required):")
    last_name = create_textbox("Last Name (optional):")
    username = create_textbox("Username (required):")

    col1, col2 = st.columns([1, 6])
    with col1:
        if create_button("Register"):
            # Validate inputs
            is_first_name_valid, first_name_error = validate_name(
                first_name, "first_name")
            is_last_name_valid, last_name_error = validate_name(
                last_name, "last_name")
            is_username_valid, username_error = validate_username(username)

            # Display errors if any validation fails
            if not is_first_name_valid:
                st.error(first_name_error)
                return
            if not is_last_name_valid:
                st.error(last_name_error)
                return
            if not is_username_valid:
                st.error(username_error)
                return

            # Attempt to register the user
            if register_user(first_name, last_name, username):
                try:
                    st.toast(
                        "Registration successful! Redirecting to login...", icon="✅")
                except AttributeError:
                    st.success(
                        "Registration successful! Redirecting to login...")
                create_navigation_button(
                    None, "login", st.session_state, trigger_redirect=True)
                st.success("Registration successful! Redirecting to login...")
                
                st.session_state["page"] = "login"
                st.rerun()
            else:
                try:
                    st.toast(
                        "Username already exists. Please choose another.", icon="❌")
                except AttributeError:
                    st.error("Username already exists. Please choose another.")
                st.error("Username already exists. Please choose another.")

    with col2:
        create_navigation_button(
            "Already have an account? Login here", "login", st.session_state)
        # Navigation button for login
        create_navigation_button("Already have an account? Login here", "login", st.session_state)
