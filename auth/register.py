# auth/register.py
import streamlit as st
import os
from dotenv import load_dotenv
from pymongo import MongoClient

from utils.validators import validate_username, validate_name  # Importing validators

# Load environment variables
load_dotenv()

# MongoDB connection
mongo_uri = os.getenv("MONGO_URI")
database_name = os.getenv("MONGO_DBNAME", "dockership")

client = MongoClient(mongo_uri)
db = client[database_name]
users_collection = db.users

def register():
    """
    Registration page where a new user can create their account. Checks for unique username and valid name format.
    """
    st.title("User Registration")

    # Form for user registration
    first_name = st.text_input("First Name (required):")
    last_name = st.text_input("Last Name (optional):")
    username = st.text_input("Username (required):")

    if st.button("Register"):
        if validate_name(first_name, "first_name") and validate_name(last_name, "last_name") and validate_username(username):
            if users_collection.find_one({"username": username}):
                st.error("Username already exists. Please choose another.")
            else:
                # Format names correctly
                first_name = first_name.capitalize()
                last_name = last_name.capitalize() if last_name else ''
                # Insert new user into the database
                users_collection.insert_one({
                    'first_name': first_name,
                    'last_name': last_name,
                    'username': username
                })
                st.success("Registration successful. Please login.")
                st.session_state.page = "login"  # Redirect to login page
        else:
            st.error("Please ensure all fields are valid.")
    
    # Go to login page
    if st.button("Go to Login Page"):
        st.session_state.page = "login"  # Set page to login
