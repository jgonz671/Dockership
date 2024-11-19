import streamlit as st

def operation():
    st.title("Operations")
    st.write("Choose a task to perform:")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Loading Task"):
            st.session_state.page = "loading"

    with col2:
        if st.button("Balancing Task"):
            st.session_state.page = "balancing"
