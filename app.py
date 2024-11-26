# app.py
"""
Main Streamlit application for the Dockership project.
Handles user interactions, navigation between pages, and session management.
"""

import os
from dotenv import load_dotenv
import streamlit as st

from config.db_config import DBConfig
from utils.state_manager import StateManager
from auth.login import login
from utils.file_handler import file_handler
from tasks.operation import operation
from tasks.loading import loading_task
from tasks.balancing import balancing_task

# Load environment variables
load_dotenv()

# Initialize MongoDB
db_config = DBConfig()
db = db_config.connect()

# Initialize session state manager
state_manager = StateManager(st.session_state)

# Page router function


def render_page(page_name):
    """
    Renders the appropriate page based on the page_name.
    """
    page_mapping = {
        "login": login,
        "file_handler": file_handler,
        "operation": operation,
        "loading": loading_task,
        "balancing": balancing_task,
    }
    # Pass database instance where needed
    page_mapping.get(page_name, login)(db)


# Main application loop
if __name__ == "__main__":
    st.set_page_config(page_title="Dockership Application", layout="wide")
    render_page(state_manager.get_page())
