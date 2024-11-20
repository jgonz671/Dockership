import streamlit as st
import pandas as pd
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection
mongo_uri = os.getenv("MONGO_URI")
database_name = os.getenv("MONGO_DBNAME", "dockership")

client = MongoClient(mongo_uri)
db = client[database_name]

log_collection = db.logs

def login():
    st.title("Dockership Login")
    st.write("Please enter your name to log in:")
    user_name = st.text_input("Name:")
    if st.button("Submit"):
        if user_name.strip():
            st.session_state.user_name = user_name
            # Log user entry in MongoDB
            log_entry = {
                'user': user_name,
                'timestamp': pd.Timestamp.now(),
                'action': "Login"
            }
            log_collection.insert_one(log_entry)
            st.success(f"Welcome, {user_name}!")
            return True
        else:
            st.error("Name cannot be empty.")
    return False
