import streamlit as st
from functions.login import login
from functions.outline import generate_content_outline
from functions.utils import ensure_session_state

st.title("Content Outline")
# Ensure session state keys exist
ensure_session_state()


# Check if the user is logged in
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
else:
    with st.expander("What is a Content Outline?"):
        st.write("Next, we need to generate a content outline for the course. This will help us structure the course content and ensure that we cover all the necessary topics.")
        st.write("You can **use the 'Generate Content Outline with ChatGPT' button to automatically generate a content outline** based on the course topic and description as you've already defined.")
        st.write("**You can then edit the outline as needed.**")
    with st.expander("Interactive Project"):
        st.write("You can choose to include an interactive project in the course. This will be a project and application of their new skills, letting students practice the material covered in the lesson.")
        project = st.toggle("Include an interactive project")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Generate Content Outline with ChatGPT"):
            with st.spinner("Generating Content Outline..."):
                generate_content_outline(project)
                outline_points = st.session_state["outline"].split("\n")
                # remove lines with only whitespace
                outline_points = [point for point in outline_points if point.strip()]
                st.session_state["outline"] = "\n".join(outline_points)
                st.session_state["outline_list"] = outline_points
    with col2:
        if st.button("Clear Content Outline", type="primary"):
            st.session_state["outline"] = ""

    outline = st.text_area(
        "Edit the generated content outline:",
        value=st.session_state["outline"],
        height=300,
    )
    st.session_state["outline"] = outline
