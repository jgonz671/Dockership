import streamlit as st
import numpy as np
import pandas as pd
from pymongo import MongoClient
import os
from dotenv import load_dotenv

from utils import file_handler
from utils.visualizer import parse_input, display_grid


# Load environment variables
load_dotenv()

# MongoDB connection
mongo_uri = os.getenv("MONGO_URI")
database_name = os.getenv("MONGO_DBNAME", "dockership")

client = MongoClient(mongo_uri)
db = client[database_name]

# Define collections
moves_collection = db.moves
log_collection = db.logs

def loading_task():
    st.title("Loading Task")
    st.write("Welcome to the Loading Task page.")

    # Ensure the file content is available in session state
    if "file_content" not in st.session_state:
        st.error("No file uploaded. Please upload a file first.")
        return

    # Retrieve file content from session state
    file_content = st.session_state.file_content

    # Parse and display the grid
    grid = parse_input(file_content.splitlines())
    display_grid(grid, title="Loading Task Layout")

    # Call the container management functionality
    # container_management_page()
