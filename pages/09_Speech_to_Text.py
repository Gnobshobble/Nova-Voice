import streamlit as st
import assemblyai as aai

aai.settings.api_key = st.secrets["ASSEMBLYAI_API_KEY"]
transcriber = aai.Transcriber()

transcript = None

if st.button("ok"):
    config = aai.TranscriptionConfig(speaker_labels=True)
    transcript = transcriber.transcribe("./output/audio_file.wav", config)
    print(transcript.text)

if transcript:
    st.write(transcript.text)