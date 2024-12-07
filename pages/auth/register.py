# pages/auth/register.py
import streamlit as st
from utils.components.buttons import create_button, create_navigation_button
from utils.components.textboxes import create_textbox
from auth.register import register_user
from utils.validators import validate_username, validate_name

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
            if validate_name(first_name, "first_name") and validate_name(last_name, "last_name") and validate_username(username):
                if register_user(first_name, last_name, username):
                    st.success("Registration successful. Please login.")
                    create_navigation_button("Proceed to Login", "login", st.session_state)
                else:
                    st.error("Username already exists. Please choose another.")
            else:
                st.error("Please ensure all fields are valid.")

    with col2:
        create_navigation_button("Already have an account? Login here", "login", st.session_state)
