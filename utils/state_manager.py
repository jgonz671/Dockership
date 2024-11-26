# utils/state_manager.py
"""
Utility module for managing Streamlit session state.
"""


class StateManager:
    """
    Manages Streamlit session state, including page navigation.
    """

    def __init__(self, session_state):
        self.session_state = session_state
        if "page" not in self.session_state:
            self.session_state.page = "login"

    def set_page(self, page_name):
        """
        Sets the current page in the session state.
        """
        self.session_state.page = page_name

    def get_page(self):
        """
        Retrieves the current page from the session state.
        """
        return self.session_state.page
