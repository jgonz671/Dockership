import streamlit as st
import numpy as np
import pandas as pd
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from modules import file_handler
from modules.visualizer import parse_input, display_grid



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

# def container_management_page():
#     # Title with custom styling
#     st.markdown("<h2 style='color: navy;'>Dockership - Container Management</h2>", unsafe_allow_html=True)

#     # Define layout
#     col1, col2 = st.columns([3, 1])

#     # Grid setup
#     num_rows, num_cols = 8, 12
#     container_grid = np.full((num_rows, num_cols), "UNUSED")
#     container_positions = {
#         (1, 3): "Pig", (2, 3): "Doe", (3, 3): "Owl",
#         (4, 3): "Ewe", (5, 3): "Cow", (6, 3): "Dog",
#         (7, 3): "Cat",
#     }

#     for (row, col), label in container_positions.items():
#         container_grid[row, col] = label

#     if "current_move" not in st.session_state:
#         st.session_state.current_move = 0
#     if "log" not in st.session_state:
#         st.session_state.log = []

#     # Retrieve moves from MongoDB or use default if not available
#     if moves_collection.count_documents({}) == 0:
#         # Insert default moves if the collection is empty
#         moves = [((1, 3), (4, 3)), ((2, 3), (5, 3)), ((3, 3), (6, 3))]
#         moves_collection.insert_many(
#             [{'source': move[0], 'target': move[1]} for move in moves])
#     else:
#         moves = [(move['source'], move['target']) for move in moves_collection.find()]

#     source_pos, target_pos = moves[st.session_state.current_move]

#     with col1:
#         st.subheader("Container Layout")
#         for row in range(num_rows):
#             cols = st.columns(num_cols)
#             for col in range(num_cols):
#                 if (row, col) == source_pos:
#                     cols[col].markdown(
#                         f"<div style='background-color:blue;color:white;text-align:center;'>{container_grid[row, col]}</div>",
#                         unsafe_allow_html=True)
#                 elif (row, col) == target_pos:
#                     cols[col].markdown(
#                         f"<div style='background-color:green;color:white;text-align:center;'>{container_grid[row, col]}</div>",
#                         unsafe_allow_html=True)
#                 else:
#                     cols[col].markdown(
#                         f"<div style='text-align:center;'>{container_grid[row, col]}</div>",
#                         unsafe_allow_html=True)

#     with col2:
#         st.subheader("Move Instructions")
#         current_container = container_grid[source_pos[0], source_pos[1]]
#         st.write(f"Move container '{current_container}' from {source_pos} to {target_pos}")
#         st.write("Estimated Time: 5 minutes")

#         if st.button("Confirm Move"):
#             move_record = {
#                 "container": current_container,
#                 "from": source_pos,
#                 "to": target_pos,
#                 "timestamp": pd.Timestamp.now().isoformat()
#             }
#             st.write("Logging move record:", move_record)  # Debugging
#             log_collection.insert_one(move_record)
#             st.session_state.log.append(f"Moved container from {source_pos} to {target_pos}")

#             if st.session_state.current_move < len(moves) - 1:
#                 st.session_state.current_move += 1
#             else:
#                 st.success("All moves completed! Please send the updated manifest to the captain.")
#                 st.balloons()
#                 if st.button("Start Over"):
#                     st.session_state.current_move = 0
#                     st.session_state.log = []

#     # Display move log
#     st.subheader("Move Log")
#     log_entries = log_collection.find()  # Retrieve log entries from MongoDB
#     for log_entry in log_entries:
#         container = log_entry.get("container", "Unknown")
#         from_pos = log_entry.get("from", "Unknown")
#         to_pos = log_entry.get("to", "Unknown")
#         timestamp = log_entry.get("timestamp", "Unknown")
#         st.write(f"{timestamp} - Moved {container} from {from_pos} to {to_pos}")


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
