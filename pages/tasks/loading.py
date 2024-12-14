import streamlit as st
from tasks.loading import (
    load_containers_with_balancer,
    unload_containers_with_balancer,
    visualize_loading,
)
from utils.grid_utils import create_ship_grid, plotly_visualize_grid
from tasks.ship_balancer import Container
from pages.tasks.balancing import visualize_steps_with_overlay, generate_animation_with_annotations
import plotly.graph_objects as go


def initialize_session_state(rows, cols):
    """
    Initializes session state variables if not already present.
    """
    if not hasattr(st.session_state, "ship_grid"):
        st.session_state.ship_grid = create_ship_grid(rows, cols)
        st.session_state.containers = []
        st.session_state.initial_plot = None
        st.session_state.final_plot = None
        st.session_state.steps = []
        st.session_state.ship_grids = []  # Store grids for steps visualization
    if not hasattr(st.session_state, "messages"):
        st.session_state.messages = []


def loading_task():
    st.title("Ship Loading and Unloading")
    st.sidebar.header("Ship Grid Setup")
    rows = 8
    cols = 12
    initialize_session_state(rows, cols)
    st.subheader("Current Ship Grid")
    plotly_visualize_grid(
        st.session_state.ship_grid, title="Ship Grid", key="current_grid"
    )
    tab = st.radio("Choose Action", ["Load Containers", "Unload Containers"], horizontal=True)

    if tab == "Load Containers":
        st.subheader("Load Containers")
        container_name = st.text_input("Container Name", placeholder="Enter container name (e.g., 'Alpha')")
        container_weight = st.number_input("Container Weight (kg)", min_value=1, step=1)
        row = st.number_input("Target Row (1-based)", min_value=1, max_value=rows, step=1) - 1
        col = st.number_input("Target Column (1-based)", min_value=1, max_value=cols, step=1) - 1

        if st.button("Load Container"):
            if container_name and container_weight > 0:
                container = Container(container_name, container_weight)
                containers_to_load = [(container, [row, col])]
                steps, ship_grids, messages = load_containers_with_balancer(
                    st.session_state.ship_grid, containers_to_load
                )
                st.session_state.ship_grid = ship_grids[-1]
                st.session_state.steps = steps
                st.session_state.ship_grids = ship_grids
                st.session_state.messages.extend(messages)
                st.success(f"Container '{container_name}' loaded successfully.")
            else:
                st.error("Please provide valid container details.")

        visualization_tab = st.radio(
            "Choose Visualization", ["Steps with Overlay", "Animated Steps"], horizontal=True
        )

        if visualization_tab == "Steps with Overlay":
            visualize_steps_with_overlay()
        elif visualization_tab == "Animated Steps":
            generate_animation_with_annotations()

    elif tab == "Unload Containers":
        st.subheader("Unload Containers")
        container_name = st.text_input("Container Name to Unload", placeholder="Enter container name (e.g., 'Alpha')")

        if st.button("Unload Container"):
            if container_name:
                steps, ship_grids, messages = unload_containers_with_balancer(
                    st.session_state.ship_grid, [container_name]
                )
                st.session_state.ship_grid = ship_grids[-1]
                st.session_state.steps = steps
                st.session_state.ship_grids = ship_grids
                st.session_state.messages.extend(messages)
                if f"Error: Container '{container_name}' not found on the grid." in messages:
                    st.error(f"Container '{container_name}' not found on the grid.")
                else:
                    st.success(f"Container '{container_name}' unloaded successfully.")
            else:
                st.error("Please provide a valid container name.")

        visualization_tab = st.radio(
            "Choose Visualization", ["Steps with Overlay", "Animated Steps"], horizontal=True
        )

        if visualization_tab == "Steps with Overlay":
            visualize_steps_with_overlay()
        elif visualization_tab == "Animated Steps":
            generate_animation_with_annotations()
