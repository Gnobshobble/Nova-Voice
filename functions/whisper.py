from openai import OpenAI
import streamlit as st
from pytube import YouTube
from moviepy.editor import AudioFileClip
import os
import ssl
import certifi

ssl_context = ssl.create_default_context(cafile=certifi.where())
ssl._create_default_https_context = ssl._create_unverified_context

def download_audio(url, path="temp_data"):
    if not os.path.exists(path):
        os.makedirs(path)
    yt = YouTube(url)
    audio_stream = yt.streams.filter(only_audio=True).first()
    audio_file = audio_stream.download(filename=f'{path}/audio.mp4')
    return audio_file

def extract_audio_segment(audio_path, start_time=0, end_time=0, output_path="temp_data/audio_segment.mp4"):
    try:
        audio = AudioFileClip(audio_path)
        # ensure start_time and end_time are within the bounds of the audio file
        if start_time <= 0 or start_time > audio.duration:
            start_time = 0
        if end_time <= 0 or end_time > audio.duration:
            end_time = audio.duration

        audio_segment = audio.subclip(start_time, end_time)
        audio_segment.write_audiofile(output_path, codec="aac")
        return output_path
    except Exception as e:
        st.error(f"Error extracting audio segment: {e}")
        return None

def transcribe_audio(audio_path="temp_data/audio.mp4"):
    try:
        # model = whisper.load_model("base.en")
        # result = model.transcribe(audio_path)
        with open(audio_path, "rb") as file:
            client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
            result = client.audio.transcriptions.create(model="whisper-1", file=file)
        return result.text
    except Exception as e:
        st.error(f"Error transcribing audio: {e}")
        return ""

def extract_information(transcript):
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    functions = [
            {
                "type": "function",
                "function":
            {
                "name": "extract_class_information",
                "description": "Extracts the hypothetical class name, scope of the course, and intended audience from the youtube video transcript.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "class_name": {
                            "type": "string",
                            "description": "The hypothetical class name."
                        },
                        "scope": {
                            "type": "string",
                            "description": "The scope of the course."
                        },
                        "intended_audience": {
                            "type": "string",
                            "description": "The intended audience for the course. This should describe the target demographic and their level of understanding of the material going into the course."
                        }
                    },
                    "required": ["class_name", "scope", "intended_audience"]
                }
            }
            }
        ]
    prompt = f"""
    You are an AI assistant helping a teacher.
    The teacher wants to extract information from a YouTube video transcript to create a structured lesson.
    ###Here's the transcript:
    {transcript}

    Extract the following information FROM THE TRANSCRIPT:
    - Hypothetical Class Name
    - Scope of the Lesson
    - Intended Audience
    """
    if transcript != "":
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are Nova, an AI teaching assistant."},
                {"role": "user", "content": prompt}
            ],
            tools=functions,
            tool_choice={"type": "function", "function": {"name": "extract_class_information"}}
        )
        return response.choices[0].message.tool_calls[0].function.arguments
    return {}
