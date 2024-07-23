import streamlit as st
import requests
from io import BytesIO
from PIL import Image, UnidentifiedImageError
from functions.login import login
from functions.multimedia import MultimediaFunctions, fetch_images, fetch_youtube_videos
from functions.utils import ensure_session_state

st.title("Multimedia Management")

# Ensure session state keys exist
ensure_session_state()

# Check if the user is logged in
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if not st.session_state.logged_in:
    login()
else:
    # Create Tabs
    tabs = st.tabs(["Autofetch", "Search", "Manual Upload", "Connections", "Review and Edit"])
    with tabs[0]:
        st.subheader("Automatically Source Multimedia from the Outline")
        st.write("We check each point in the outline, and do additional searches to find relevant images and videos to include in the course content.")
        # Outline is saved in session state as a string
        video_bool = st.checkbox("Include YouTube Videos")
        image_bool = st.checkbox("Include Images")
        if st.button("Fetch Multimedia"):
            with st.spinner("Fetching multimedia..."):
                # Fetch multimedia from outline
                multimedia = MultimediaFunctions(image_bool, video_bool)
                multimedia.pull_key_topics(st.session_state["outline_list"])
                image_list, video_list = multimedia.search_multimedia()
                st.session_state["images"].extend(image_list)
                st.session_state["videos"].extend(video_list)
            st.success("Multimedia fetched successfully!")
            with st.expander("View Multimedia", expanded=True):
                # Display the fetched multimedia
                image_urls, image_titles = [], []
                for img in st.session_state["images"]:
                    image_urls.append(img["url"])
                    image_titles.append(img["title"])
                video_urls, video_titles = [], []
                for video in st.session_state["videos"]:
                    video_urls.append(video["url"])
                    video_titles.append(video["title"])

                c1, c2 = st.columns(2)
                with c1:
                    st.write("Images:")
                    st.write(image_urls)
                    st.write("Videos:")
                    st.write(video_urls)
                with c2:
                    st.write("Images:")
                    st.write(image_titles)
                    st.write("Videos:")
                    st.write(video_titles)

    with tabs[1]:
        # Automatically Fetched Multimedia
        st.header("Search for Multimedia")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Fetch YouTube Videos")
            query = st.text_input("Search for YouTube videos related to the topic:")
            max_results = st.number_input(
                "Number of videos to fetch:", min_value=1, max_value=10, value=3
            )
            max_duration = st.number_input(
                "Maximum video length (in minutes):", min_value=1, max_value=60, value=5
            )
            if st.button("Fetch YouTube Videos"):
                st.session_state["fetched_videos"] = fetch_youtube_videos(
                    query, max_results, max_duration
                )

            if "fetched_videos" in st.session_state:
                for video in st.session_state["fetched_videos"]:
                    st.video(video["url"])
                    if st.button(f'Include {video["title"]}', key=video["url"]):
                        if video not in st.session_state["videos"]:
                            st.session_state["videos"].append(video)
                            st.success(f"Added {video}")
        with col2:
            st.subheader("Fetch Images")
            image_query = st.text_input("Search for images related to the topic:")
            max_image_results = st.number_input("Number of images to fetch:", min_value=1, max_value=10, value=3)
            if st.button("Fetch Images"):
                st.session_state["fetched_images"] = fetch_images(image_query, max_image_results)

            if "fetched_images" in st.session_state:
                for img_url in st.session_state["fetched_images"]:
                    if img_url not in st.session_state["images"]:
                        try:
                            response = requests.get(img_url["url"])
                            response.raise_for_status()
                            content_type = response.headers.get("Content-Type")
                            if "image" in content_type:
                                img = Image.open(BytesIO(response.content))
                                st.image(img, caption=img_url["title"])
                                if st.button(f'Include image {img_url["title"]}', key=img_url["url"]):
                                    st.session_state["images"].append(img_url)
                                    st.success(f"Added {img_url}")
                            else:
                                st.error(f"URL is not an image: {img_url}")
                        except (UnidentifiedImageError, requests.RequestException) as e:
                            st.error(f"Could not load image from {img_url}: {e}")

    with tabs[2]:
        # Manual Uploads
        st.header("Manual Uploads")
        st.write("Paste links to multimedia you want to include in the course.")
        manual_videos = st.text_area("Enter YouTube video links (one per line):", value="")
        if st.button("Add Manual Videos"):
            st.session_state["videos"].extend(manual_videos.split("\n"))

        manual_images = st.text_area("Enter image links (one per line):", value="")
        if st.button("Add Manual Images"):
            st.session_state["images"].extend(manual_images.split("\n"))





    with tabs[3]:
        # Associating points from the outline with specific materials
        st.header("Associate Outline Points with Materials")
        with st.expander("What are Connections?"):
            st.write("Connections are associations between outline points and multimedia materials. You can associate images and videos with specific points in the outline to guarantee a material is associated with specific course content.")
            st.write("For example, you can associate an image of a semicolon with a point in the outline introducing semicolons. This ensures the image is displayed when the course content reaches that point.")

        outline_points = st.session_state["outline"].split('\n')

        # remove empty strings from outline points
        outline_points = [point for point in outline_points if point]

        video_titles, image_titles = [], []
        for video in st.session_state["videos"]:
            string = "Video: " + str(video["title"])
            video_titles.append(string)
        for image in st.session_state["images"]:
            string = "Image: " + str(image["title"])
            image_titles.append(string)

        selected_material = st.selectbox("Select a material to associate:", options=video_titles + image_titles)

        selected_point = st.selectbox("Select an outline point to associate with the material:", options=st.session_state["outline_list"])
        if st.button("Associate"):
            if selected_point and selected_material:
                if selected_point not in st.session_state["associations"]:
                    st.session_state["associations"][selected_point] = []
                st.session_state["associations"][selected_point].append(selected_material)

        st.write("Current Associations:")
        st.json(st.session_state["associations"])

    with tabs[4]:
        # Review and Edit tab
        st.header("Review and Edit")
        st.write("Review your associations and uploads here. Remove any links that you don't want to include in the lesson.")
        video_titles = [video["title"] for video in st.session_state["videos"]]
        image_titles = [image["title"] for image in st.session_state["images"]]
        st.write("Manual Uploads and Automatically Fetched Videos:", video_titles)
        st.write("Manual Uploads and Automatically Fetched Images:", image_titles)
        st.write("Associations:", st.session_state["associations"])

        # Remove Videos
        st.subheader("Remove Videos")
        video_to_remove = st.selectbox("Select a video to remove:", options=st.session_state["videos"])
        if st.button("Remove Video"):
            if video_to_remove in st.session_state["videos"]:
                st.session_state["videos"].remove(video_to_remove)
                # Remove from associations
                for key in st.session_state["associations"]:
                    if video_to_remove in st.session_state["associations"][key]:
                        st.session_state["associations"][key].remove(video_to_remove)
                st.success("Video removed and associations updated.")

        # Remove Images
        st.subheader("Remove Images")
        image_to_remove = st.selectbox("Select an image to remove:", options=st.session_state["images"])
        if st.button("Remove Image"):
            if image_to_remove in st.session_state["images"]:
                st.session_state["images"].remove(image_to_remove)
                # Remove from associations
                for key in st.session_state["associations"]:
                    if image_to_remove in st.session_state["associations"][key]:
                        st.session_state["associations"][key].remove(image_to_remove)
                st.success("Image removed and associations updated.")
