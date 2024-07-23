import time

import streamlit as st
from functions.home_automations import (
    automated_page_one,
    automated_page_two,
    automated_page_three,
    automated_page_four
)
from functions.utils import ensure_session_state
from functions.login import login

st.set_page_config(page_title="Curriculum Builder", layout="wide")

# Ensure session state keys exist
ensure_session_state()


# Function to handle login
# Check if the user is logged in
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
else:
# Display title and description
# Display title and description
    st.title("Curriculum Builder")
    st.write(
        "Welcome to the Curriculum Builder! You can choose to automatically generate the curriculum using the button below, or manually work step-by-step following the pages on the side."
    )
    col1, col2 = st.columns(2)
    with col1:
        with st.expander("Automated Curriculum Creation"):
            st.write("You can automatically create a course by inputting a YouTube video link below.")
            st.write("*You can edit it once it's all completed.*")
        youtube_link = st.text_input(
            "Enter a YouTube video link to get started:", key="youtube_link"
        )
        with st.expander("Optional: Time Range"):
            st.write("If you want to extract content from a specific segment of the video, input the start and end times below.")
            col3, col4 = st.columns(2)
            with col3:
                start_time_input = st.number_input(
                    "Start time (in seconds):", key="start_time_input"
                )
            with col4:
                end_time_input = st.number_input(
                    "End time (in seconds):", key="end_time_input"
                )

    with col2:
        #links manually to page 1
        # st.write("This is a placeholder path to the first page of the curriculum builder.")
        with st.expander("Manual Curriculum Creation"):
            st.write("Click the button below to start building your curriculum step-by-step.")
        # st.page_link("pages/01_Course_Meta.py", label="**Curriculum Builder**", use_container_width=True)
        if st.button("Start Curriculum Builder"):
            st.switch_page("pages/01_Course_Meta.py")

    if st.button("Create Course..."):
        start_time = time.time()
        with st.status(
            "Course Creation Status", expanded=True, state="running"
        ) as status:
            error_occurred = False

            # Run automated process from each page
            try:
                automated_page_one(status, youtube_link, start_time_input, end_time_input)
                st.write("Course Metadata successfully collected!")
            except Exception as e:
                status.update(label="Error!", state="error")
                st.error(f"An error occurred: {e}")
                error_occurred = True

            if not error_occurred:
                try:
                    automated_page_two(status)
                    st.write("Course outline defined!")
                except Exception as e:
                    status.update(label="Error!", state="error")
                    st.error(f"An error occurred: {e}")
                    error_occurred = True

            if not error_occurred:
                try:
                    automated_page_three(status)
                    st.write("Multimedia successfully sourced!")
                except Exception as e:
                    status.update(label="Error!", state="error")
                    st.error(f"An error occurred: {e}")
                    error_occurred = True

            if not error_occurred:
                try:
                    automated_page_four(status)
                    st.write("Hamsters are warmed up and ready!")
                except Exception as e:
                    status.update(label="Error!", state="error")
                    st.error(f"An error occurred: {e}")
                    error_occurred = True

            # Update final status only if no error occurred
            if not error_occurred:
                status.update(label="Course created!", state="complete", expanded=False)
                st.write(f"Course created in {time.time() - start_time:.2f} seconds.")
