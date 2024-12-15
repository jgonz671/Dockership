import streamlit as st
from tasks.ship_loader import load_containers, unload_containers, convert_grid_to_manuscript, append_outbound_to_filename
from utils.grid_utils import create_ship_grid, plotly_visualize_grid
from utils.logging import LogFileManager  # Import Log Manager
from config.db_config import DBConfig
from utils.components.buttons import create_navigation_button
import os

# Initialize MongoDB and Log Manager
db_config = DBConfig()
db = db_config.connect()
logs_collection = db_config.get_collection("logs")
log_manager = LogFileManager(logs_collection)

def initialize_session_state(rows, cols):
    """
    Initializes Streamlit session state variables.
    """
    if "ship_grid" not in st.session_state:
        st.session_state.ship_grid = create_ship_grid(rows, cols)
        log_manager.log("Ship grid initialized.", "info")
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "total_cost" not in st.session_state:
        st.session_state.total_cost = 0

def loading_task():
    """
    Streamlit page for loading, unloading containers, and exporting the ship grid.
    """
    col1, _ = st.columns([2, 8])  # Center the button
    with col1:
        if create_navigation_button("Back to Operations", "operation", st.session_state):
            log_manager.log("Navigated back to operations.", "info")
            st.rerun()

    st.title("Ship Loading and Unloading System")
    log_manager.log("Loading task started.", "info")

    # Initialize session state
    rows, cols = 8, 12
    initialize_session_state(rows, cols)

    # Display current grid
    st.subheader("Current Ship Grid")
    plotly_visualize_grid(st.session_state.ship_grid, title="Ship Grid")

    # Action selection
    tab = st.radio("Choose Action", ["Load Containers", "Unload Containers", "Export Manuscript"], horizontal=True)

    if tab == "Load Containers":
        st.subheader("Load Containers")
        container_names_input = st.text_input(
            "Container Names (comma-separated)",
            placeholder="Enter container names (e.g., Alpha,Beta,Gamma)"
        )

        if st.button("Load Containers"):
            if container_names_input:
                container_names = [name.strip() for name in container_names_input.split(",")]
                log_manager.log(f"Attempting to load containers: {container_names}", "info")

                updated_grid, messages, cost = load_containers(
                    st.session_state.ship_grid, container_names
                )
                st.session_state.ship_grid = updated_grid  # Update session state
                st.session_state.messages.extend(messages)
                st.session_state.total_cost += cost

                for message in messages:
                    if "Error" in message:
                        st.error(message)
                        log_manager.log(message, "error")
                    else:
                        st.success(message)
                        log_manager.log(message, "info")

                plotly_visualize_grid(
                    st.session_state.ship_grid, title="Updated Ship Grid"
                )
            else:
                st.error("Please provide valid container names.")
                log_manager.log("Load containers failed: No container names provided.", "warning")

    elif tab == "Unload Containers":
        st.subheader("Unload Containers")
        container_names_input = st.text_input(
            "Container Names to Unload (comma-separated)",
            placeholder="Enter container names (e.g., Alpha,Beta,Gamma)"
        )

        if st.button("Unload Containers"):
            if container_names_input:
                container_names = [name.strip() for name in container_names_input.split(",")]
                log_manager.log(f"Attempting to unload containers: {container_names}", "info")

                updated_grid, messages, cost = unload_containers(
                    st.session_state.ship_grid, container_names
                )
                st.session_state.ship_grid = updated_grid  # Update session state
                st.session_state.messages.extend(messages)
                st.session_state.total_cost += cost

                for message in messages:
                    if "Error" in message:
                        st.error(message)
                        log_manager.log(message, "error")
                    else:
                        st.success(message)
                        log_manager.log(message, "info")

                plotly_visualize_grid(
                    st.session_state.ship_grid, title="Updated Ship Grid"
                )
            else:
                st.error("Please provide valid container names.")
                log_manager.log("Unload containers failed: No container names provided.", "warning")

    elif tab == "Export Manuscript":
        st.subheader("Export Ship Grid to Manuscript")

        # Generate manuscript from the current grid
        manuscript = convert_grid_to_manuscript(st.session_state.ship_grid)
        log_manager.log("Exporting ship grid to manuscript.", "info")

        # Display manuscript in a text area for review
        st.text_area("Manuscript Preview", manuscript, height=300)

        # Input filename
        filename_input = st.text_input("Filename (without extension)", "ship_grid")
        if st.button("Download Manuscript"):
            if filename_input.strip():
                # Create filename with OUTBOUND appended
                filename = append_outbound_to_filename(f"{filename_input}.txt")

                # Save manuscript to a file
                with open(filename, "w") as file:
                    file.write(manuscript)

                log_manager.log(f"Manuscript exported to file: {filename}", "info")

                # Allow user to download the file
                with open(filename, "rb") as file:
                    st.download_button(
                        label="Download Manuscript",
                        data=file,
                        file_name=filename,
                        mime="text/plain"
                    )
            else:
                st.error("Please provide a valid filename.")
                log_manager.log("Export manuscript failed: Invalid filename provided.", "warning")

    # Display total cost and action history
    st.subheader("Operation Summary")
    st.info(f"Total Operation Cost: {st.session_state.total_cost} seconds")

    st.subheader("Action History")
    for msg in st.session_state.messages:
        st.write(msg)
