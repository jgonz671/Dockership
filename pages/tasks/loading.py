import streamlit as st
from tasks.loading import load_containers, unload_containers
from pages.tasks.balancing import plotly_visualize_grid
from utils.grid_utils import create_ship_grid


def initialize_session_state(rows, cols):
    """
    Initializes session state variables if not already present.
    """
    if "ship_grid" not in st.session_state:
        st.session_state.ship_grid = create_ship_grid(rows, cols)
    if "messages" not in st.session_state:
        st.session_state.messages = []  # Initialize messages as an empty list


def loading_task():
    st.title("Ship Loading and Unloading System")

    # Initialize session state
    rows, cols = 8, 12  # Fixed grid size
    initialize_session_state(rows, cols)

    # Display current grid
    st.subheader("Current Ship Grid")
    st.plotly_chart(plotly_visualize_grid(st.session_state.ship_grid, title="Ship Grid"), use_container_width=True)

    # Action Tabs
    tab = st.radio("Choose Action", ["Load Containers", "Unload Containers"], horizontal=True)

    if tab == "Load Containers":
        st.subheader("Load Containers")

        # Input container details
        container_names_input = st.text_input(
            "Container Names (comma-separated)",
            placeholder="Enter container names (e.g., Alpha,Beta,Gamma)"
        )

        if st.button("Load Containers"):
            if container_names_input:
                container_names = [name.strip() for name in container_names_input.split(",")]
                messages = load_containers(st.session_state.ship_grid, container_names)
                st.session_state.messages.extend(messages)

                for message in messages:
                    if "Error" in message:
                        st.error(message)
                    else:
                        st.success(message)

                # Update grid visualization
                st.plotly_chart(plotly_visualize_grid(st.session_state.ship_grid, title="Updated Ship Grid"), use_container_width=True)
            else:
                st.error("Please provide valid container details.")

    elif tab == "Unload Containers":
        st.subheader("Unload Containers")

        # Input container names to unload
        container_names_input = st.text_input(
            "Container Names to Unload (comma-separated)",
            placeholder="Enter container names (e.g., Alpha,Beta,Gamma)"
        )

        if st.button("Unload Containers"):
            if container_names_input:
                container_names = [name.strip() for name in container_names_input.split(",")]
                messages = unload_containers(st.session_state.ship_grid, container_names)
                st.session_state.messages.extend(messages)

                for message in messages:
                    if "Error" in message:
                        st.error(message)
                    else:
                        st.success(message)

                # Update grid visualization
                st.plotly_chart(plotly_visualize_grid(st.session_state.ship_grid, title="Updated Ship Grid"), use_container_width=True)
            else:
                st.error("Please provide valid container names.")

    # Action Messages
    st.subheader("Action Messages")
    for msg in st.session_state.messages:
        st.write(msg)
