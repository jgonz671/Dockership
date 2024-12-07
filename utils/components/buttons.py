# Dockership/utils/components/buttons.py
import streamlit as st

def create_button(label, on_click=None, args=None, **kwargs):
    """
    Creates a customizable Streamlit button.

    Args:
        label (str): The text to display on the button.
        on_click (function, optional): A function to call when the button is clicked.
        args (tuple, optional): Arguments to pass to the `on_click` function.
        **kwargs: Additional keyword arguments to customize the button appearance (e.g., style, icon).

    Returns:
        bool: Whether the button was clicked.
    """
    button = st.button(label, on_click=on_click, args=args, **kwargs)
    return button

def create_navigation_button(label, page_name, session_state, **kwargs):
    """
    Creates a navigation button that changes the page in the session state.

    Args:
        label (str): The text to display on the button.
        page_name (str): The page name to navigate to.
        session_state (dict): The Streamlit session state.
        **kwargs: Additional keyword arguments to customize the button appearance.

    Returns:
        bool: Whether the button was clicked.
    """
    def navigate():
        session_state["page"] = page_name  # Modify the session state to trigger rerun.

    return create_button(label, on_click=navigate, **kwargs)

def create_logout_button(session_state):
    """
    Creates a logout button that clears the session state and redirects to the login page.

    Args:
        session_state (dict): The Streamlit session state.

    Returns:
        bool: Whether the logout button was clicked.
    """
    def logout():
        session_state.clear()  # Clears all session state variables.
        session_state["page"] = "login"  # Redirect to the login page.

    return create_button("Logout", on_click=logout)
