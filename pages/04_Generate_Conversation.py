import streamlit as st
from functions.conversation import ConversationSimulator
from functions.login import login
from functions.utils import ensure_session_state
import os

# Ensure session state keys exist
ensure_session_state()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
else:

    st.title("Generate an Example Conversation")
    st.write("This tool generates an example conversation between a student and a teacher. You can use this as a preview of the conversational style of the course content.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Generate Conversation"):
            with st.spinner("Generating Example Lesson..."):
                conversation_sim = ConversationSimulator()
                conversation = conversation_sim.simulate_conversation()
            st.session_state["conversation"] = conversation
    with col2:
        if st.button("Clear Conversation", type="primary"):
            st.session_state["conversation"] = ""
    # Display the generated conversation in a text area
    conversation = st.text_area("Generated Conversation:", value=st.session_state["conversation"], height=400)
    st.html('<br>')
    st.page_link("pages/05_Test_Drive.py", label="Take your course for a spin!", icon="➡️")
