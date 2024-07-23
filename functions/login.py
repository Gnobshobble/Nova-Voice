import streamlit as st
import time


def login():
    st.title("Login")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if password == st.secrets["PASSWORD"]:
            st.session_state.logged_in = True
            st.success("Login successful")
            time.sleep(1)
            st.rerun()
        else:
            st.error("Invalid password")
