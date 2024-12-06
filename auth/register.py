# auth/register.py
import streamlit as st
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from utils.validators import validate_username, validate_name
from utils.navigation import navigate_to  

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

    first_name = st.text_input("First Name (required):")
    last_name = st.text_input("Last Name (optional):")
    username = st.text_input("Username (required):")

    col1, col2 = st.columns([1, 6])
    with col1:
        if st.button("Register"):
            if validate_name(first_name, "first_name") and validate_name(last_name, "last_name") and validate_username(username):
                if users_collection.find_one({"username": username}):
                    st.error("Username already exists. Please choose another.")
                else:
                    first_name = first_name.capitalize()
                    last_name = last_name.capitalize() if last_name else ''
                    users_collection.insert_one({
                        'first_name': first_name,
                        'last_name': last_name,
                        'username': username
                    })
                    st.success("Registration successful. Please login.")
                    navigate_to("login") 
            else:
                st.error("Please ensure all fields are valid.")

    with col2:
        if st.button("Already have an account? Login here"):
            navigate_to("login")  
