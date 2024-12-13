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

def create_navigation_button(label, page_name, session_state, trigger_redirect=False, **kwargs):
    """
    Creates a navigation button that changes the page in the session state.

    Args:
        label (str): The text to display on the button.
        page_name (str): The page name to navigate to.
        session_state (dict): The Streamlit session state.
        trigger_redirect (bool): If True, navigates immediately without requiring a button click.
        **kwargs: Additional keyword arguments to customize the button appearance.

    Returns:
        bool: Whether the button was clicked (only for non-trigger_redirect mode).
    """
    def navigate():
        session_state["page"] = page_name

    if trigger_redirect:
        navigate()  # Immediately set the navigation page.
    else:
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

        # Floating logout message (if Streamlit supports `st.toast`, otherwise fallback to success message)
        try:
            st.toast("Logout successful!", icon="✅")
        except AttributeError:
            st.success("Logout successful!")

    return create_button("Logout", on_click=logout)

def create_centered_buttons(label_left, label_right, action_left, action_right):
    """
    Creates two buttons on the same horizontal line, centered to the page, equidistant from each other.

    Args:
        label_left (str): Text for the left button.
        label_right (str): Text for the right button.
        action_left (function): Function to execute on clicking the left button.
        action_right (function): Function to execute on clicking the right button.
    """
    col1, col2 = st.columns(2, gap="large")
    with col1:
        if create_button(label_left, on_click=action_left):
            return "left_clicked"

    with col2:
        if create_button(label_right, on_click=action_right):
            return "right_clicked"

    return None
