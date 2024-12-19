import streamlit as st

def initialize_data():
    """Initialize session state for shared variables."""

    if "VARG1" not in st.session_state:
        st.session_state.VARG1 = []

    if "VARG2" not in st.session_state:
        st.session_state.VARG2 = []

    if "VARG3" not in st.session_state:
        st.session_state.VARG3 = []
