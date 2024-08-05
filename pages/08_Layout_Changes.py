import streamlit as st

from openai import OpenAI
import requests

from streamlit_extras.bottom_container import bottom
from audiorecorder import audiorecorder
from streamlit_TTS import auto_play

from prompts.test_drive import system_prompt, opening_message

from functions.login import login
from functions.utils import ensure_session_state

from re import findall

st.title("Test Drive the Course!")
if not st.session_state.get("default_text"):
    st.session_state.default_text = "some text"

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def load_course(info):
    # Re-fetch the session_state variables
    updated_topic = st.session_state.get("class_name", "")
    updated_recent_conversation = st.session_state.get("conversation", "")
    if (
        updated_topic != info["topic"]
        or updated_recent_conversation != info["recent_conversation"]
    ):
        info["topic"] = updated_topic
        info["recent_conversation"] = updated_recent_conversation
    # Refresh the prompts with the new topic and conversation
    formatted_system_prompt = system_prompt.format(
        topic=info["topic"], recent_conversation=info["recent_conversation"]
    )
    formatted_opening_message = opening_message.format(topic=info["topic"])
    # Reset the message log
    st.session_state["messages"] = []
    st.session_state["messages"] = [
        {"role": "system", "content": formatted_system_prompt, "latex": None}
    ]
    st.session_state["messages"].append(
        {"role": "assistant", "content": formatted_opening_message, "latex": None}
    )

def save_lesson(info):
    URL = st.secrets["BACKEND_URL"]
    API_KEY = st.secrets["BACKEND_API_KEY"]

    data = {
        "name": info["topic"],
        "description": info["description"],
        "opener": info["opener"],
        "conversation": info["recent_conversation"],
    }
    headers = {"x-authentication": API_KEY}
    response = requests.post(URL, json=data, headers=headers)

    if response.ok:
        st.success("Course sent to Nova successfully!")
    else:
        st.error(f"Failed to send course to Nova: {response.text}")

def get_tts_output(tts_input):
    with client.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice=st.session_state["tts_voice"],
        speed=st.session_state["tts_speed"],
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

def render_latex(latex_to_render):
    if latex_to_render:
        with st.popover("Latex Preview"):
            st.text("Latex Preview")
            for latex in latex_to_render:
                latex = latex[2:-2]
                st.latex(latex)

def render_message(id, message):
    with st.container():
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                spacing, tts = st.columns([0.9, 0.1])
                if tts.button("🔊", key=id):
                    get_tts_output(message["content"])
                st.markdown(message["content"])
                render_latex(message["latex"])

def render_messages():
    for index, message in enumerate(st.session_state["messages"]):
        render_message(index, message)

def get_latex_from_message(text):
    # check if text contains LaTeX inline delimiters "\(...\)" "\[...\]"
    return findall(r"\\\(.*?\\\)|\\\[.*?\\\]", text)

def receive_response(prompt):
    stream = client.chat.completions.create(
    model="gpt-4o",
        messages=[
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ],
    stream=True,
    )
    spacing, tts = st.columns([0.9, 0.1])
        
    with st.chat_message("assistant"):
       response =  st.write_stream(stream)
       if tts.button("🔊", key=len(st.session_state["messages"])) or st.session_state["tts_autoplay"]:
            get_tts_output(response)
       latex = get_latex_from_message(response)
       st.session_state.messages.append({"role": "assistant", "content": response, "latex": latex})
       render_latex(latex)

def send_message(prompt):
    latex = get_latex_from_message(prompt)
    print(latex)
    st.session_state.messages.append({"role": "user", "content": prompt, "latex": latex})
    print(st.session_state["messages"][len(st.session_state.messages) - 1])
        
    render_message(len(st.session_state["messages"]) - 1, {"role": "user", "content": prompt, "latex": latex})
    receive_response(prompt)

def get_transcription(wav_audio_data):
    wav_audio_data.export("output/audio_file.wav", format="wav")

    audio_file= open("output/audio_file.wav", "rb")
    transcription = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file
     )
    return transcription.text

def settings():
    voices = ("alloy", "echo", "fable", "onyx", "nova", "shimmer")
    st.header("Settings")
    st.session_state["tts_voice"] = st.selectbox(
        "Choose a voice:",  
        voices,
        index = voices.index(st.session_state["tts_voice"])
    )
    st.session_state["tts_speed"] = st.slider(
        "Set the playback speed:",
          0.25, 2.0, st.session_state["tts_speed"]
    )
    st.session_state["tts_autoplay"] = st.toggle("Enable autoplay", value=st.session_state["tts_autoplay"])

def load_content():
    st.write(
        "Welcome to the Test Drive! This is the fully-formatted course loaded into Nova, your AI teaching assistant. You can interact with Nova to see how the course would be presented to students."
    )

    ensure_session_state()
    topic = st.session_state.get("class_name", "")

    conversation_info = {
        "topic":  topic,
        "recent_conversation": st.session_state.get("conversation", ""),
        "description": st.session_state.get("scope", ""),
        "opener": opening_message.format(topic=topic)
    }

    col1, col2, col3 = st.columns(3)
    with col1:
        # Load the most recently generated conversation
        if st.button("Load Course 📦"):
            load_course(conversation_info)
    st.empty()
    with col2:
        if st.button("Save the lesson! 💾 ", type="primary"):
            save_lesson(conversation_info)
    with col3:
        with st.popover("Settings ⚙️"):
            settings()

    render_messages()

    with bottom():
        wav_audio_data = audiorecorder("", "")
        if "audio_data" not in st.session_state:
            st.session_state.audio_data = wav_audio_data
        chat_input = st.chat_input("Take your course for a spin!")

    if chat_input:
        send_message(chat_input)
    elif not wav_audio_data == st.session_state.audio_data and len(wav_audio_data) > 0:
        transcript = get_transcription(wav_audio_data)
        send_message(transcript)
        st.session_state.audio_data = wav_audio_data

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
else:
    load_content()