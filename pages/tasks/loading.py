import streamlit as st
from utils.visualizer import plotly_visualize_grid
from tasks.loading import (
    load_container_by_name,
    unload_container_by_name,
    visualize_loading,
)
from utils.grid_utils import create_ship_grid
from utils.log_manager import LogFileManager  # Import LogFileManager
from config.db_config import DBConfig  # For MongoDB connection

# Initialize LogFileManager
db_config = DBConfig()
db = db_config.connect()
log_manager = LogFileManager(db)

def loading_task():
    st.title("Ship Loading and Unloading")

    # Sidebar for grid setup
    st.sidebar.header("Ship Grid Setup")
    rows = 8
    cols = 12

    # Initialize the ship grid in session state
    if "ship_grid" not in st.session_state:
        st.session_state.ship_grid = create_ship_grid(rows, cols)
        log_manager.write_log("Initialized ship grid.")

    # Initialize messages in session state
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # Display current grid
    st.subheader("Current Ship Grid")
    plotly_visualize_grid(st.session_state.ship_grid, title="Ship Grid", key="current_grid")

    # Tab selection for Load/Unload functionality
    tab = st.radio("Choose Action", ["Load Containers", "Unload Containers"], horizontal=True)

    if tab == "Load Containers":
        st.subheader("Load Containers")

        # Input for container details
        container_name = st.text_input("Container Name", placeholder="Enter container name (e.g., 'Alpha')")
        container_weight = st.number_input("Container Weight (kg)", min_value=1, step=1)
        row = st.number_input("Target Row (1-based)", min_value=1, max_value=rows, step=1) - 1
        col = st.number_input("Target Column (1-based)", min_value=1, max_value=cols, step=1) - 1

        if st.button("Load Container"):
            if container_name and container_weight > 0:
                message = load_container_by_name(
                    st.session_state.ship_grid,
                    container_name,
                    container_weight,
                    [row, col],
                )
                st.session_state["messages"].append(message)
                log_manager.write_log(message)  # Log the loading action
                st.success(message)
            else:
                st.error("Please provide valid container details.")
                log_manager.write_log("Invalid container details provided for loading.", "warning")

        # Display messages
        st.subheader("Action Messages")
        for msg in st.session_state["messages"]:
            st.write(msg)

        # Refresh grid visualization
        visualize_loading(st.session_state.ship_grid, title="Ship Grid After Loading")

    elif tab == "Unload Containers":
        st.subheader("Unload Containers")

        # Input for container to unload
        container_name = st.text_input("Container Name to Unload", placeholder="Enter container name (e.g., 'Alpha')")

        if st.button("Unload Container"):
            if container_name:
                message, location = unload_container_by_name(st.session_state.ship_grid, container_name)
                st.session_state["messages"].append(message)
                log_manager.write_log(message)  # Log the unloading action
                if location:
                    st.success(message)
                else:
                    st.error(message)
            else:
                st.error("Please provide a valid container name.")
                log_manager.write_log("Invalid container name provided for unloading.", "warning")

        # Display messages
        st.subheader("Action Messages")
        for msg in st.session_state["messages"]:
            st.write(msg)

        # Refresh grid visualization
        visualize_loading(st.session_state.ship_grid, title="Ship Grid After Unloading")


if __name__ == "__main__":
    loading_task()
