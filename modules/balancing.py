import streamlit as st

def balancing_task():
    st.title("Balancing Task")
    st.write("Performing the balancing task. This is where your logic will go.")
    if st.button("Back to Operations"):
        st.session_state.page = "operation"
