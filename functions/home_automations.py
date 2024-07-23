from functions.utils import clean_temp_data
from functions.whisper import (
    download_audio,
    transcribe_audio,
    extract_information,
    extract_audio_segment,
)
from functions.outline import generate_content_outline
from functions.multimedia import MultimediaFunctions
from functions.conversation import ConversationSimulator
import json
import streamlit as st


def automated_page_one(status, youtube_link, start, end):
    if youtube_link:
        status.update(label="Downloading and Transcribing YouTube video...")
        download_audio(youtube_link)
        if start >= 0 and end > 0 and start < end:
            extract_audio_segment("temp_data/audio.mp4", start, end)
            transcript = transcribe_audio("temp_data/audio_segment.mp4")
        else:
            transcript = transcribe_audio()
        st.session_state["transcript"] = transcript
        st.session_state["knowledge_base"] = transcript
        status.update(label="Extracting Information...")
        raw_extracted_information = extract_information(transcript)
        extracted_information = json.loads(raw_extracted_information)
        st.session_state["class_name"] = extracted_information["class_name"]
        st.session_state["scope"] = extracted_information["scope"]
        st.session_state["audience"] = extracted_information["intended_audience"]
        clean_temp_data()
    else:
        st.warning("Please enter a YouTube video link to proceed.")

def automated_page_two(status):
    status.update(label="Generating Content Outline...")
    generate_content_outline(project_component=False)
    outline_list =  st.session_state["outline"].split("\n")
    outline_list = [item for item in outline_list if item.strip()]
    st.session_state["outline_list"] = outline_list

def automated_page_three(status):
    status.update(label="Sourcing Relevant Multimedia...")
    multimedia = MultimediaFunctions(include_images=True)
    multimedia.pull_key_topics(st.session_state["outline_list"])
    image_list, video_list = multimedia.search_multimedia()
    for video in video_list:
        st.session_state["videos"].append(video)
    for image in image_list:
        st.session_state["images"].append(image)

def automated_page_four(status):
    status.update(label="Giving our hamsters a break...")
    con_sim = ConversationSimulator()
    conversation = con_sim.simulate_conversation()
    st.session_state["conversation"] = conversation
