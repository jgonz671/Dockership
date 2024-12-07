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
            is_valid, error_message = validate_username(username)
            if not is_valid:
                try:
                    st.toast(error_message, icon="❌")
                except AttributeError:
                    st.error(error_message)
                return

            user = check_user_exists(username)
            if user:
                st.session_state.user_name = user['username']
                st.session_state.first_name = user['first_name']
                log_user_action(username, "Login")  # Log user entry in MongoDB
                try:
                    st.toast(f"Welcome, {user['first_name']}!", icon="✅")
                except AttributeError:
                    st.success(f"Welcome, {user['first_name']}!")
                create_navigation_button(None, "file_handler", st.session_state, trigger_redirect=True)
            else:
                try:
                    st.toast("Username not found. Please register.", icon="❌")
                except AttributeError:
                    st.error("Username not found. Please register.")

    with col2:
        create_navigation_button("Need an account? Register here", "register", st.session_state)
