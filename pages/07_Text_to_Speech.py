import streamlit as st
from openai import OpenAI
import pyaudio

st.title("Text to Speech")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
tts_output = None

def get_tts_output():
    p = pyaudio.PyAudio()
    stream = p.open(format=8, channels=1, rate=24_000, output=True)

    with client.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice=tts_voice,
        input=tts_input,
        response_format="pcm"
    ) as response:
        for chunk in response.iter_bytes(1024):
            stream.write(chunk)

with st.form("OpenAI TTS"):
    tts_input = st.text_area("Input text to read aloud", placeholder="Enter text here...", max_chars=4096)
    tts_voice = st.selectbox("Choose your voice", ("alloy", "echo", "fable", "onyx", "nova", "shimmer"), index=None, placeholder="Choose a voice...")
    
    if st.form_submit_button():
        if not tts_input:
            st.error('No text inputed')
        elif not tts_voice:
            st.error('No voice inputed')
        else:
            with st.spinner("Retrieving text to speech output..."):
                tts_output = get_tts_output()

    



