# auth/login.py
import streamlit as st
import os
import pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient

from utils.validators import validate_username  # Importing validators

# Load environment variables
load_dotenv()

# MongoDB connection
mongo_uri = os.getenv("MONGO_URI")
database_name = os.getenv("MONGO_DBNAME", "dockership")

client = MongoClient(mongo_uri)
db = client[database_name]
users_collection = db.users
log_collection = db.logs

def login():
    """
    Login page for users. Validates username, checks database for existence, and saves user data to session state.
    """
    st.title("Dockership Login")
    st.write("Please enter your username to log in:")

    # Username regex pattern: only letters, numbers, @, _, .
    username = st.text_input("Username:")

    if st.button("Login"):
        if validate_username(username):
            user = users_collection.find_one({"username": username})
            if user:
                st.session_state.user_name = user['username']
                st.session_state.first_name = user['first_name']
                # Log user entry in MongoDB
                log_entry = {
                    'user': username,
                    'timestamp': pd.Timestamp.now(),
                    'action': "Login"
                }
                log_collection.insert_one(log_entry)
                st.success(f"Welcome, {user['first_name']}!")
                st.session_state.page = "file_handler"  # Redirect to file handler page
            else:
                st.error("Username not found. Please register.")
        else:
            st.error("Invalid username format. Please enter a valid username.")
    
    # Go to register page
    if st.button("Go to Register Page"):
        st.session_state.page = "register"  # Set page to register
