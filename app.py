import os
from dotenv import load_dotenv
import streamlit as st
from pymongo import MongoClient
from datetime import datetime

# Set page config at the very beginning
st.set_page_config(page_title="Dockership Application", layout="wide")

# Import pages and components
from config.db_config import DBConfig
from utils.state_manager import StateManager
from pages.auth.login import login
from pages.auth.register import register
from pages.file_handler.file_handler import file_handler
from pages.tasks.operation import operation
from pages.tasks.balancing import balancing_page

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

# MongoDB collections
manifest_collection = db.manifest
action_logs_collection = db.action_logs

# Enhanced Loading Task

def loading_task():
    """
    Streamlit page for the loading task with manifest and logging functionality.
    """
    st.title("Dockership - Manifest and Logs")

    # Manifest Section
    st.subheader("Current Manifest")
    manifest = list(manifest_collection.find({}, {"_id": 0}))
    if manifest:
        st.write(manifest)
    else:
        st.write("No containers in the manifest.")

    # Action Logging Section
    st.subheader("Action Logs")
    logs = list(action_logs_collection.find({}, {"_id": 0}))
    if logs:
        st.write(logs)
    else:
        st.write("No actions logged yet.")

    # Container Operations
    st.subheader("Manage Containers")
    with st.form("container_form"):
        container_id = st.text_input("Container ID")
        weight = st.number_input("Weight", min_value=0.0, step=1.0)
        position = st.text_input("Position (e.g., 1,3)")
        action = st.selectbox("Action", ["Load", "Unload"])
        submit_button = st.form_submit_button("Submit")

        if submit_button:
            if action == "Load":
                try:
                    position_tuple = tuple(map(int, position.split(',')))
                    manifest_collection.insert_one({
                        "container_id": container_id,
                        "weight": weight,
                        "position": position_tuple,
                        "status": "loaded",
                        "timestamp": datetime.utcnow()
                    })
                    action_logs_collection.insert_one({
                        "action": "load",
                        "container_id": container_id,
                        "position": position_tuple,
                        "timestamp": datetime.utcnow(),
                        "notes": f"Loaded container {container_id} at position {position_tuple}."
                    })
                    st.success(f"Container {container_id} loaded at position {position_tuple}.")
                except Exception as e:
                    st.error(f"Error loading container: {e}")
            elif action == "Unload":
                try:
                    result = manifest_collection.update_one(
                        {"container_id": container_id},
                        {"$set": {"status": "unloaded", "timestamp": datetime.utcnow()}}
                    )
                    if result.matched_count == 0:
                        st.warning(f"Container {container_id} not found in manifest.")
                    else:
                        action_logs_collection.insert_one({
                            "action": "unload",
                            "container_id": container_id,
                            "timestamp": datetime.utcnow(),
                            "notes": f"Unloaded container {container_id}."
                        })
                        st.success(f"Container {container_id} unloaded.")
                except Exception as e:
                    st.error(f"Error unloading container: {e}")

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
    render_page(state_manager.get_page())
