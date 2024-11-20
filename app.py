import os
from pymongo import MongoClient
from dotenv import load_dotenv
import streamlit as st
import numpy as np
import pandas as pd
from modules import login, file_handler, operation, loading, balancing

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

# Define app state for multi-page navigation
if "page" not in st.session_state:
    st.session_state.page = "login"
if "user_name" not in st.session_state:
    st.session_state.user_name = None

def login_page():
    if login.login():  # If login is successful
        st.session_state.page = "file_handler"  # Navigate to file handler

def file_handler_page():
    if file_handler.file_handler():  # If file upload is successful
        st.session_state.page = "operation"

def operation_page():
    operation.operation()  # Render operation page

def loading_page():
    loading.loading_task() 
    if st.button("Go Back"):
        st.session_state.page = "operation"

def balancing_page():
    st.title("Balancing Task")
    st.write("Performing balancing task...")
    if st.button("Go Back"):
        st.session_state.page = "operation"

# Route pages based on session state
if st.session_state.page == "login":
    login_page()
elif st.session_state.page == "file_handler":
    file_handler_page()
elif st.session_state.page == "operation":
    operation_page()
elif st.session_state.page == "loading":
    loading_page()
elif st.session_state.page == "balancing":
    balancing_page()
