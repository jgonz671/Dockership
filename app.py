import streamlit as st
import numpy as np
import pandas as pd
# Ensure db_config.py is correctly set up as previously discussed
from modules.db_config import get_db

# Initialize MongoDB connection
db = get_db()
moves_collection = db.moves  # Collection for moves
log_collection = db.logs  # Collection for logs

# Title with custom styling
st.markdown("<h2 style='color: navy;'>Dockership - Container Management</h2>",
            unsafe_allow_html=True)

# Define layout
col1, col2 = st.columns([3, 1])

# Grid setup
num_rows, num_cols = 8, 12
container_grid = np.full((num_rows, num_cols), "UNUSED")
container_positions = {
    (1, 3): "Pig", (2, 3): "Doe", (3, 3): "Owl",
    (4, 3): "Ewe", (5, 3): "Cow", (6, 3): "Dog",
    (7, 3): "Cat",
}

for (row, col), label in container_positions.items():
    container_grid[row, col] = label

if "current_move" not in st.session_state:
    st.session_state.current_move = 0
if "log" not in st.session_state:
    st.session_state.log = []

# Retrieve moves from MongoDB or use default if not available
if moves_collection.count_documents({}) == 0:
    # Insert default moves if the collection is empty
    moves = [((1, 3), (4, 3)), ((2, 3), (5, 3)), ((3, 3), (6, 3))]
    moves_collection.insert_many(
        [{'source': move[0], 'target': move[1]} for move in moves])
else:
    moves = [(move['source'], move['target'])
             for move in moves_collection.find()]

source_pos, target_pos = moves[st.session_state.current_move]

with col1:
    st.subheader("Container Layout")
    for row in range(num_rows):
        cols = st.columns(num_cols)
        for col in range(num_cols):
            if (row, col) == source_pos:
                cols[col].markdown(
                    f"<div style='background-color:blue;color:white;text-align:center;'>{container_grid[row, col]}</div>", unsafe_allow_html=True)
            elif (row, col) == target_pos:
                cols[col].markdown(
                    f"<div style='background-color:green;color:white;text-align:center;'>{container_grid[row, col]}</div>", unsafe_allow_html=True)
            else:
                cols[col].markdown(
                    f"<div style='text-align:center;'>{container_grid[row, col]}</div>", unsafe_allow_html=True)

with col2:
    st.subheader("Move Instructions")
    current_container = container_grid[source_pos[0], source_pos[1]]
    st.write(
        f"Move container '{current_container}' from {source_pos} to {target_pos}")
    st.write("Estimated Time: 5 minutes")

    if st.button("Confirm Move"):
        move_record = {
            'container': current_container,
            'from': source_pos,
            'to': target_pos,
            'timestamp': pd.Timestamp.now()
        }
        log_collection.insert_one(move_record)
        st.session_state.log.append(
            f"Moved container from {source_pos} to {target_pos}")

        if st.session_state.current_move < len(moves) - 1:
            st.session_state.current_move += 1
        else:
            st.success(
                "All moves completed! Please send the updated manifest to the captain.")
            st.balloons()
            if st.button("Start Over"):
                st.session_state.current_move = 0
                st.session_state.log = []

# Display move log
st.subheader("Move Log")
log_entries = log_collection.find()  # Retrieve log entries from MongoDB
for log_entry in log_entries:
    st.write(
        f"{log_entry['timestamp']} - Moved {log_entry['container']} from {log_entry['from']} to {log_entry['to']}")
