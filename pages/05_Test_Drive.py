import requests
import streamlit as st
from functions.login import login
from openai import OpenAI
import re
from prompts.test_drive import system_prompt, opening_message
from functions.utils import ensure_session_state
from openai import OpenAI
from prompts.test_drive import opening_message, system_prompt

st.title("Test Drive the Course!")

def get_latex_from_message(text):
    # check if text contains LaTeX inline delimiters "\(...\)" "\[...\]"
    latex = re.findall(r"\\\(.*?\\\)|\\\[.*?\\\]", text)
    return latex

def render_messages(single_message=None):
    if single_message:
        with st.container():
            if single_message["role"] != "system":
                with st.chat_message(single_message["role"]):
                    st.markdown(single_message["content"])
    else:
        with st.container():
            for message in st.session_state["messages"]:
                if message["role"] != "system":
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])


# Check if the user is logged in
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
else:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    st.write(
        "Welcome to the Test Drive! This is the fully-formatted course loaded into Nova, your AI teaching assistant. You can interact with Nova to see how the course would be presented to students."
    )

    # Ensure session state keys exist
    ensure_session_state()
    URL = st.secrets["BACKEND_URL"]
    API_KEY = st.secrets["BACKEND_API_KEY"]

    topic = st.session_state.get("class_name", "")
    recent_conversation = st.session_state.get("conversation", "")
    description = st.session_state.get("scope", "")
    opener = opening_message.format(topic=topic)

    col1, col2 = st.columns(2)
    with col1:
        # Load the most recently generated conversation
        if st.button("Load Course"):
            # Re-fetch the session_state variables
            updated_topic = st.session_state.get("class_name", "")
            updated_recent_conversation = st.session_state.get("conversation", "")
            if (
                updated_topic != topic
                or updated_recent_conversation != recent_conversation
            ):
                topic = updated_topic
                recent_conversation = updated_recent_conversation
            # Refresh the prompts with the new topic and conversation
            formatted_system_prompt = system_prompt.format(
                topic=topic, recent_conversation=recent_conversation
            )
            formatted_opening_message = opening_message.format(topic=topic)
            # Reset the message log
            st.session_state["messages"] = []
            st.session_state["messages"] = [
                {"role": "system", "content": formatted_system_prompt}
            ]
            st.session_state["messages"].append(
                {"role": "assistant", "content": formatted_opening_message}
            )
    st.empty()
    st.toggle(label="toggle_label", key="toggle_TTS")
    with col2:
        if st.button("Save the lesson!", type="primary"):
            data = {
                "name": topic,
                "description": description,
                "opener": opener,
                "conversation": recent_conversation,
            }
            headers = {"x-authentication": API_KEY}
            response = requests.post(URL, json=data, headers=headers)

            if response.ok:
                st.success("Course sent to Nova successfully!")
            else:
                st.error(f"Failed to send course to Nova: {response.text}")

    
    # Render messages except for the system prompt
    render_messages()

    if prompt := st.chat_input("Take your course for a spin!"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        render_messages(single_message={"role": "user", "content": prompt})
        with st.container():
            with st.chat_message("assistant"):
                stream = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ],
                    stream=True,
                )
                response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})
        # re render the most recent message with LaTeX previews
        latex_to_render = get_latex_from_message(response)
        if latex_to_render:
            with st.popover("Latex Preview"):
                st.text("Latex Preview")
                for latex in latex_to_render:
                    latex = latex[2:-2]
                    st.latex(latex)