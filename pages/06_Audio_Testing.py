import streamlit as st

st.title("Test Some Audio!")

audio_file = st.file_uploader("Choose an audio file", type=['mp3', 'wav', 'ogg'])

if audio_file:
    st.audio(audio_file, format=f"audio/{audio_file.type}")
    
    