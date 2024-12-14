import streamlit as st
from tasks.ship_loader import load_containers, unload_containers
from utils.grid_utils import create_ship_grid, plotly_visualize_grid

def initialize_session_state(rows, cols):
    if "ship_grid" not in st.session_state:
        st.session_state.ship_grid = create_ship_grid(rows, cols)
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "total_cost" not in st.session_state:
        st.session_state.total_cost = 0

def loading_task():
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
        container_names_input = st.text_input(
            "Container Names (comma-separated)",
            placeholder="Enter container names (e.g., Alpha,Beta,Gamma)"
        )

        if st.button("Load Containers"):
            if container_names_input:
                container_names = [name.strip() for name in container_names_input.split(",")]
                messages, cost = load_containers(st.session_state.ship_grid, container_names)
                st.session_state.messages.extend(messages)
                st.session_state.total_cost += cost

                for message in messages:
                    if "Error" in message:
                        st.error(message)
                    else:
                        st.success(message)

                plotly_visualize_grid(st.session_state.ship_grid, title="Updated Ship Grid")
            else:
                st.error("Please provide valid container names.")

    elif tab == "Unload Containers":
        st.subheader("Unload Containers")
        container_names_input = st.text_input(
            "Container Names to Unload (comma-separated)",
            placeholder="Enter container names (e.g., Alpha,Beta,Gamma)"
        )

        if st.button("Unload Containers"):
            if container_names_input:
                container_names = [name.strip() for name in container_names_input.split(",")]
                messages, cost = unload_containers(st.session_state.ship_grid, container_names)
                st.session_state.messages.extend(messages)
                st.session_state.total_cost += cost

                for message in messages:
                    if "Error" in message:
                        st.error(message)
                    else:
                        st.success(message)

                plotly_visualize_grid(st.session_state.ship_grid, title="Updated Ship Grid")
            else:
                st.error("Please provide valid container names.")

    # Display total cost and action history
    st.subheader("Operation Summary")
    st.info(f"Total Operation Cost: {st.session_state.total_cost} seconds")
    
    st.subheader("Action History")
    for msg in st.session_state.messages:
        st.write(msg)