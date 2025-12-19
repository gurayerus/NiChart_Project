import streamlit as st

st.session_state.setdefault(
    'count', 0
)

st.write(st.session_state)
