from pages.tasks.balancing import balancing_page
from pages.tasks.loading import loading_task
from pages.tasks.operation import operation
from pages.file_handler.file_handler import file_handler
from pages.auth.register import register
from pages.auth.login import login
from utils.state_manager import StateManager
from config.db_config import DBConfig
import os
from dotenv import load_dotenv
import streamlit as st

# Set page config at the very beginning
st.set_page_config(page_title="Dockership Application", layout="wide")

# Import pages and components

# Load environment variables
load_dotenv()

# Initialize MongoDB
db_config = DBConfig()
db = db_config.connect()

# Check database connection
if db_config.check_connection():
    st.sidebar.success("✅ Connected to MongoDB successfully.")
else:
    st.sidebar.error(
        "❌ Failed to connect to MongoDB. Check your configuration.")
    st.stop()

# Initialize session state manager
state_manager = StateManager(st.session_state)

# Page router function


def render_page(page_name):
    """
    Renders the appropriate page based on the page_name.
    """
    page_mapping = {
        "login": login,
        "register": register,
        "file_handler": file_handler,
        "operation": operation,
        "loading": loading_task,
        "balancing": balancing_page
    }

    # Render the appropriate page
    page_mapping.get(page_name, login)()


# Main application loop
if __name__ == "__main__":
    if "updated_grid" not in st.session_state:
        st.session_state["updated_grid"] = None  # Store the most recent grid
    render_page(state_manager.get_page())
