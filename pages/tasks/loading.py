import streamlit as st
from tasks.ship_loader import load_containers, unload_containers
from utils.grid_utils import create_ship_grid, plotly_visualize_grid
from utils.components.buttons import create_navigation_button
from tasks.balancing_utils import convert_grid_to_manifest, append_outbound_to_filename
import os


def initialize_session_state(rows, cols):
    if "ship_grid" not in st.session_state:
        st.session_state.ship_grid = create_ship_grid(rows, cols)
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "total_cost" not in st.session_state:
        st.session_state.total_cost = 0
    if "container_weights" not in st.session_state:
        st.session_state.container_weights = {}
    if "loading_step" not in st.session_state:
        st.session_state.loading_step = "input_names"  
    if "container_names_to_load" not in st.session_state:
        st.session_state.container_names_to_load = []
    if "updated_manifest" not in st.session_state:
        st.session_state.updated_manifest = ""
    if "outbound_filename" not in st.session_state:
        st.session_state.outbound_filename = "manifest.txt"

def reset_loading_state():
    st.session_state.loading_step = "input_names"
    st.session_state.container_names_to_load = []
    st.session_state.container_weights = {}

def loading_task():
    col1, _ = st.columns([2, 8])  # Center the button
    with col1:
        if create_navigation_button("Back to Operations", "operation", st.session_state):
            st.rerun()

    st.title("Ship Loading and Unloading System")

    # Initialize session state
    rows, cols = 8, 12
    initialize_session_state(rows, cols)

    # Display current grid
    st.subheader("Current Ship Grid")
    plotly_visualize_grid(st.session_state.ship_grid, title="Ship Grid")

    # Action selection
    tab = st.radio("Choose Action", ["Load Containers", "Unload Containers"], horizontal=True)

    if tab == "Load Containers":
        st.subheader("Load Containers")

        if st.session_state.loading_step == "input_names":
            # Step 1: Input Container Names
            container_names_input = st.text_input(
                "Container Names (comma-separated)",
                placeholder="Enter container names (e.g., Alpha,Beta,Gamma)"
            )

            if st.button("Next"):
                if container_names_input:
                    container_names = [name.strip() for name in container_names_input.split(",") if name.strip()]
                    if not container_names:
                        st.error("Please provide valid container names.")
                    else:
                        st.session_state.container_names_to_load = container_names
                        st.session_state.loading_step = "input_weights"
                        st.rerun()
                else:
                    st.error("Please provide valid container names.")

        elif st.session_state.loading_step == "input_weights":
            # Step 2: Input Weights for Each Container
            st.subheader("Enter Container Weights")
            container_weights = {}
            for name in st.session_state.container_names_to_load:
                if name not in st.session_state.container_weights:
                    st.session_state.container_weights[name] = 0.0  
                st.session_state.container_weights[name] = st.number_input(
                    f"Weight for '{name}' (kg):",
                    min_value=0,
                    max_value=99999,
                    step=1,
                    format="%d",
                    key=f"{name}_weight"
                )

            if st.button("Confirm Load"):
                # Proceed to load containers with the provided weights
                container_names = st.session_state.container_names_to_load
                container_weights = st.session_state.container_weights
                messages, cost = load_containers(st.session_state.ship_grid, container_names, container_weights)
                st.session_state.messages.extend(messages)
                st.session_state.total_cost += cost
                reset_loading_state()
                st.rerun()

    elif tab == "Unload Containers":
        st.subheader("Unload Containers")
        container_names_input = st.text_input(
            "Container Names to Unload (comma-separated)",
            placeholder="Enter container names (e.g., Alpha,Beta,Gamma)"
        )

        if st.button("Unload Containers"):
            if container_names_input:
                container_names = [name.strip()
                                   for name in container_names_input.split(",")]
                updated_grid, messages, cost = unload_containers(
                    st.session_state.ship_grid, container_names)
                st.session_state.ship_grid = updated_grid  # Update session state
                st.session_state.messages.extend(messages)
                st.session_state.total_cost += cost

                for message in messages:
                    if "Error" in message:
                        st.error(message)
                    else:
                        st.success(message)

                plotly_visualize_grid(
                    st.session_state.ship_grid, title="Updated Ship Grid")
            else:
                st.error("Please provide valid container names.")

    # Display total cost and action history
    st.subheader("Operation Summary")
    st.info(f"Total Operation Cost: {st.session_state.total_cost} seconds")

    # Force manifest update button
    st.subheader("Update/Download Manifest")
    if st.button("Update Manifest"):
        updated_manifest = convert_grid_to_manifest(st.session_state.ship_grid)
        outbound_filename = append_outbound_to_filename(
            st.session_state.get("file_name", "manifest.txt")
        )
        st.session_state.updated_manifest = updated_manifest
        st.session_state.outbound_filename = outbound_filename
        st.success("Manifest updated successfully!")

    # Provide download button
    st.download_button(
        label="Download Updated Manifest",
        data=st.session_state.updated_manifest,
        file_name=st.session_state.outbound_filename,
        mime="text/plain",
    )

    st.subheader("Action History")
    for msg in st.session_state.messages:
        st.write(msg)