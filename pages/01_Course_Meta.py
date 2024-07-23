import json

import streamlit as st
from functions.login import login
from functions.utils import clean_temp_data, ensure_session_state
from functions.whisper import download_audio, extract_information, transcribe_audio


st.title("Class and Topic Management")

# Ensure session state keys exist
ensure_session_state()

# Check if the user is logged in
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
else:
    tabs = st.tabs(["Start from a Source", "Start from Scratch", "Knowledge Base (Optional)"])

    with tabs[0]:
        st.write("If you have any source material, such as a YouTube video, PDF, or other content, that you want to use as the basis of the class you can upload it here.")
        st.write("We'll extract the information for you!")
        # single_source_file = st.file_uploader("Upload a file:", key="single_source_file")
        youtube_link = st.text_input(
            "Enter a YouTube video link to get started:", key="youtube_link"
        )

        if st.button("Submit"):
            # if single_source_file is not None:
            #     process_single_source(single_source_file
            with st.spinner("Downloading and Transcribing YouTube video..."):
                download_audio(youtube_link)
                transcript = transcribe_audio()
                st.session_state["transcript"] = transcript
                st.session_state["knowledge_base"] = transcript
                raw_extracted_information = extract_information(transcript)
                extracted_information = json.loads(raw_extracted_information)
                st.session_state["class_name"] = extracted_information["class_name"]
                st.session_state["scope"] = extracted_information["scope"]
                st.session_state["audience"] = extracted_information["intended_audience"]

            st.success("Information extracted successfully!")
            with st.expander("Extracted Information"):
                st.write(extracted_information)
            clean_temp_data()
            st.info("You can now proceed to the next step.")

    with tabs[1]:
        # st.subheader("Name")
        with st.expander("Name"):
            st.write("Enter the name of the class, this will be the title of the course the students will see, and should describe the content of the course.")
            st.write("For example, *'Conflict Resolution in Organizations'* or *'Semicolon: The Underdog of Punctuation'*.")
        class_name = st.text_input("Enter the name of the class:", value=st.session_state["class_name"])
        st.session_state["class_name"] = class_name

        with st.expander("Scope"):
            st.write("Define the scope of the course, this should describe the topics that will be covered in the course.")
            st.write("For example, *'This course will cover the basics of conflict resolution, including identifying conflicts, resolving conflicts, and preventing conflicts.'*")
        scope = st.text_area("Define the scope of the course:", value=st.session_state["scope"])
        st.session_state["scope"] = scope

        with st.expander("Audience"):
            st.write("Describe the intended audience for the course. This should describe the target demographic and their level of understanding of the material going into the course.")
            st.write("For example, *'This course is intended for professionals who are new to conflict resolution and want to learn the basics.'*")
        audience = st.text_input("Who is the intended audience (Age, Experience):", value=st.session_state["audience"])
        st.session_state["audience"] = audience


    with tabs[2]:
        st.header("Knowledge Base (Optional)")
        st.write("If you have any other reference materials, you can upload them here.")
        uploaded_files = st.file_uploader(
            "Upload reference materials (PDFs, Videos, etc.):",
            accept_multiple_files=True,
        )
        if uploaded_files:
            st.session_state["knowledge_base"] = [file.name for file in uploaded_files]
