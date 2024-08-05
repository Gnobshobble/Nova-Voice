import requests
import streamlit as st
from functions.login import login
from openai import OpenAI
import re
from prompts.test_drive import system_prompt, opening_message
from functions.utils import ensure_session_state
from openai import OpenAI
from audiorecorder import audiorecorder
from openai import OpenAI
from streamlit_extras.bottom_container import bottom
from streamlit_TTS import auto_play

st.title("Test Drive the Course!")
if not st.session_state.get("default_text"):
    st.session_state.default_text = "some text"

def get_latex_from_message(text):
    # check if text contains LaTeX inline delimiters "\(...\)" "\[...\]"
    latex = re.findall(r"\\\(.*?\\\)|\\\[.*?\\\]", text)
    return latex


def render_messages(single_message=None, button_id=None):
    if single_message:
        with message_box.container():
            if single_message["role"] != "system":
                with st.chat_message(single_message["role"]):
                    spacing, tts = st.columns([0.9, 0.1])
                    if tts.button("🔊", key=button_id):
                        get_tts_output('alloy', single_message["content"])
                    st.markdown(single_message["content"])
    else:
        with message_box.container():
            for index, message in enumerate(st.session_state["messages"]):
                if message["role"] != "system":
                    with message_box.chat_message(message["role"]):
                        spacing, tts = st.columns([0.9, 0.1])
                        if tts.button("🔊", key=index):
                            get_tts_output('alloy', message["content"])
                        st.markdown(message["content"])

def receive_response():
    with message_box.chat_message("assistant"):
        stream = client.chat.completions.create(
            model="gpt-4o",
             messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
         )
        spacing, tts = st.columns([0.9, 0.1])
        
        response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})
        if tts.button("🔊", key="latest_model_response"):
            get_tts_output('alloy', response)
        return response
    
def get_tts_output(tts_voice, tts_input):
    with client.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice=tts_voice,
        input=tts_input,
        response_format="wav"
    ) as response:
        with open("output/output.wav", "wb") as file:
            for chunk in response.iter_bytes(1024):
                file.write(chunk)

    audio = {
        'bytes': None,
        'sample_rate': 24000,
        'sample_width': 2
    }

    with open('output/output.wav', 'rb') as f:
        audio['bytes'] = f.read()

    auto_play(audio, wait=False, key=None)


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

    
    # Render messages except for the syst
    message_box = st.container()
    render_messages()
    with bottom():
        wav_audio_data = audiorecorder("", "")
        chat_input = st.chat_input("Take your course for a spin!")

    sample = None
    client = OpenAI()
    if len(wav_audio_data) > 0:
        wav_audio_data.export("output/audio_file.wav", format="wav")

        audio_file= open("output/audio_file.wav", "rb")
        transcription = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file
        )
        sample = transcription.text
        wav_audio_data = None

    
    print(chat_input)
    print(sample)

    if (sample or chat_input):
        if (chat_input): 
            prompt = chat_input
        else:
            prompt = sample
            sample = None

        st.session_state.messages.append({"role": "user", "content": prompt})
        
        render_messages(single_message={"role": "user", "content": prompt}, button_id=len(st.session_state["messages"]))
        response = receive_response()
        
        # re render the most recent message with LaTeX previews
        latex_to_render = get_latex_from_message(response)
        if latex_to_render:
            with st.popover("Latex Preview"):
                st.text("Latex Preview")
                for latex in latex_to_render:
                    latex = latex[2:-2]
                    st.latex(latex)
            
            
