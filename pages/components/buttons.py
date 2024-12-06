# pages/components/buttons.py
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
        session_state.page = page_name
        st.experimental_rerun()

    return create_button(label, on_click=navigate, **kwargs)

