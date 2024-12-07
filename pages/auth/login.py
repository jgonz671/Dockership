# pages/auth/login.py
import streamlit as st
from utils.components.buttons import create_button, create_navigation_button
from utils.components.textboxes import create_textbox
from auth.login import check_user_exists, log_user_action

def login():
    """
    Login page for users. Validates username, checks database for existence, and saves user data to session state.
    """
    st.title("Dockership Login")
    st.write("Please enter your username to log in:")

    username = create_textbox("Username:")

    # Create two buttons aligned on the same row at opposite ends
    col1, col2 = st.columns([1, 1])
    with col1:
        if create_button("Login"):
            if username:  # Check if username is not empty
                user = check_user_exists(username)
                if user:
                    st.session_state.user_name = user['username']
                    st.session_state.first_name = user['first_name']
                    log_user_action(username, "Login")  # Log user entry in MongoDB
                    st.success(f"Welcome, {user['first_name']}!")
                    create_navigation_button("Proceed to File Handler", "file_handler", st.session_state)
                else:
                    st.error("Username not found. Please register.")
            else:
                st.error("Username cannot be empty.")

    with col2:
        create_navigation_button("Need an account? Register here", "register", st.session_state)
