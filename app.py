import os
from dotenv import load_dotenv
import streamlit as st

# Set page config at the very beginning
st.set_page_config(page_title="Dockership Application", layout="wide")

# Import pages and components
from config.db_config import DBConfig
from utils.state_manager import StateManager
from pages.auth.login import login
from pages.auth.register import register
from pages.file_handler.file_handler import file_handler

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
    }

    # Render the appropriate page
    page_mapping.get(page_name, login)()


# Main application loop
if __name__ == "__main__":
    render_page(state_manager.get_page())
