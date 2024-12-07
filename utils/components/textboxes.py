# Dockership/utils/components/textboxes.py
import streamlit as st

def create_textbox(label, default_value="", key=None, **kwargs):
    """
    Creates a customizable text input box.

    Args:
        label (str): The label to display next to the textbox.
        default_value (str): The default value for the textbox (default is empty string).
        key (str, optional): The Streamlit key for the widget (if provided, it can be used to store the state separately).
        **kwargs: Additional keyword arguments to customize the textbox (e.g., placeholder, max_chars).

    Returns:
        str: The text entered by the user.
    """
    return st.text_input(label, value=default_value, key=key, **kwargs)

def create_password_box(label, default_value="", key=None, **kwargs):
    """
    Creates a customizable password input box.

    Args:
        label (str): The label to display next to the password box.
        default_value (str): The default value for the password box (default is empty string).
        key (str, optional): The Streamlit key for the widget (if provided, it can be used to store the state separately).
        **kwargs: Additional keyword arguments to customize the password box (e.g., max_chars).

    Returns:
        str: The password entered by the user.
    """
    return st.text_input(label, value=default_value, type="password", key=key, **kwargs)

