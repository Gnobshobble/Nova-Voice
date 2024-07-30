import streamlit as st
from openai import OpenAI
from pydub.playback import play
from pydub import AudioSegment


if "audio_playing" not in st.session_state:
    st.session_state["audio_playing"] = False



st.title("Text to Speech")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
tts_output = None

def get_tts_output():
    with client.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice=tts_voice,
        input=tts_input,
        response_format="wav"
    ) as response:
        with open("temp_data/output.wav", "wb") as file:
            for chunk in response.iter_bytes(1024):
                file.write(chunk)

    st.audio("temp_data/output.wav", "audio/wav")

    
with st.form("OpenAI TTS"):
    tts_input = st.text_area("Input text to read aloud", placeholder="Enter text here...", max_chars=4096)
    tts_voice = st.selectbox("Choose your voice", ("alloy", "echo", "fable", "onyx", "nova", "shimmer"), index=None, placeholder="Choose a voice...")
    
    if st.form_submit_button():
        if not tts_input:
            st.error('No text inputted')
        elif not tts_voice:
            st.error('No voice inputted')
        else:
            with st.spinner("Retrieving text to speech output..."):
                get_tts_output()


button_container = st.container()
playback = st.empty()

def bool_switch():
    if st.session_state.audio_playing:
        playback.image("temp_data/muted.png")
        st.session_state.audio_playing = False
    else:
        playback.image("temp_data/speaking.png")
        st.session_state.audio_playing = True

with button_container:
    if st.button("Play Audio"):
        audio = AudioSegment.from_file("temp_data/output.wav")
        bool_switch()
        play(audio)
        bool_switch()