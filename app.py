import os
from dotenv import load_dotenv
import streamlit as st

# Initialize Streamlit's page config at the very beginning
st.set_page_config(page_title="Dockership Application", layout="wide")

# Import pages and components
from config.db_config import DBConfig
from utils.state_manager import StateManager
from pages.auth.login import login
from pages.auth.register import register
from pages.file_handler.file_handler import file_handler
from pages.tasks.operation import operation
from pages.tasks.loading import loading_task
from pages.tasks.balancing import balancing_task

# Load environment variables
load_dotenv()

# Initialize MongoDB
db_config = DBConfig()
db = db_config.connect()

# Check database connection
if db_config.check_connection():
    st.sidebar.success("✅ Connected to MongoDB successfully.")
else:
    st.sidebar.error("❌ Failed to connect to MongoDB. Check your configuration.")
    st.stop()  # Stop the application if the database connection fails.

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
        "balancing": balancing_task,
    }
    
    # Call the page based on the current session state
    page_mapping.get(page_name, login)()

# Main application loop
if __name__ == "__main__":
    render_page(state_manager.get_page())
