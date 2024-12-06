# utils/navigation.py
import streamlit as st

def navigate_to(page_name):
    """
    Updates the session state page and triggers a rerun.
    """
    st.session_state.page = page_name
    st.experimental_rerun()
