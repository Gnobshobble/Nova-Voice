import os
import streamlit as st

def clean_temp_data(folder="temp_data"):
    """
    Cleans the temporary data folder by removing all files within it.
    """
    for file in os.listdir(folder):
        file_path = os.path.join(folder, file)
        os.remove(file_path)

def ensure_session_state():
    for key, default_value in session_state_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

session_state_defaults = {
    "class_name": "",
    "scope": "",
    "audience": "",
    "knowledge_base": [],
    "transcript": "",
    "videos": [],
    "images": [],
    "outline": "",
    "outline_list": [],
    "associations": {},
    "conversation": "",
    "messages": [],
}
