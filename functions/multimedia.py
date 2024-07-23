from openai import OpenAI
import streamlit as st
import os
from prompts.multimedia import multimedia_instructions, multimedia_function
import json
from googleapiclient.discovery import build
import isodate
import re

class MultimediaFunctions:
    def __init__(self, include_images=False, include_videos=False):
        self.client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        self.function = multimedia_function
        self.include_images = include_images
        self.include_videos = include_videos
        self.outline = st.session_state.get("outline", "")

    def pull_key_topics(self, outline):
        # returns a list of topics from the outline that could use a visual aid
        self.topic_search_terms = []
        history = []
        for point in outline:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": multimedia_instructions},
                    {"role": "user", "content": "### History:\n" + str(history)},
                    {"role": "user", "content": "### Next Topic:\n" + str(point)}
                ],
                tools=self.function,
                tool_choice={"type": "function", "function": {"name": "extract_multimedia_info"}}
            )
            try:
                response_json = json.loads(response.choices[0].message.tool_calls[0].function.arguments)
                history.append(f"Topic: {point}, Including Multimedia: {response_json['should_search']}")
                self.topic_search_terms.append(response_json)
            except:
                print("Error parsing JSON:")
                print(response.choices[0].message.tool_calls[0].function.arguments)
        return self.topic_search_terms


    def search_multimedia(self):
        # search for multimedia based on the key topics
        # return a list of links
        video_list = []
        image_list = []
        if self.include_images:
            for item in self.topic_search_terms:
                if item["should_search"].lower() == "yes":
                    try:
                        images = fetch_images(item["search_term"], 2)
                    except:
                        images = [{"url": "https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png", "title": "Placeholder Google Image", "source": "google.com"}]

                    for image in images:
                        image_list.append(image)
                    self.create_associations(item["topic"], images)

        if self.include_videos:
            for item in self.topic_search_terms:
                if item["should_search"].lower() == "yes":
                    try:
                        videos = fetch_youtube_videos(item["search_term"], 1, 3)
                    except:
                        videos = [{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "title": "Never Gonna Give You Up", "snippet": "Rick Astley - Never Gonna Give You Up (Official Music Video)", "source": "youtube.com"}]

                    for video in videos:
                        video_list.append(video)
                    self.create_associations(item["topic"], videos)
        # print the percentage of topics that have multimedia
        # do this by counting number of "should_search" == "yes" and dividing by total number of topics
        total_topics = len(self.topic_search_terms)
        topics_with_multimedia = len([item for item in self.topic_search_terms if item["should_search"].lower() == "yes"])
        percentage = topics_with_multimedia / total_topics * 100
        st.toast(f"Percentage of topics with multimedia: {percentage}%")
        return image_list, video_list

    def create_associations(self, topic, multimedia_links):
        # create associations between multimedia and the key topics
        for link in multimedia_links:
            if topic not in st.session_state["associations"]:
                st.session_state["associations"][topic] = []
            st.session_state["associations"][topic].append(link["url"])



# Fetching Images
def fetch_images(query, max_results):
    api_key = st.secrets["GOOGLE_API_KEY"]
    cse_id = st.secrets["CSE_ID"]

    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(
        q=query,
        cx=cse_id,
        searchType="image",
        num=max_results,
        safe="off"
    ).execute()

    image_data = []
    for item in res.get("items", []):
        title = item.get("title")
        if title:
            # Remove any characters after a '-' or '|' using regex
            title = re.split(r'[-|]', title)[0].strip()

        data = {
            "url": item["link"],
            "title": title,
            "snippet": item.get("snippet"),
            "source": item.get("displayLink")
        }
        image_data.append(data)
    return image_data

# Fetching YouTube Videos
def fetch_youtube_videos(query, max_results, max_duration):
    youtube = build('youtube', 'v3', developerKey=st.secrets["YOUTUBE_API_KEY"])
    request = youtube.search().list(
        q=query,
        part='snippet',
        type='video',
        maxResults=max_results * 2,  # Fetch more results to filter out already included videos
        videoDuration='short' if max_duration <= 4 else 'medium'
    )
    response = request.execute()

    videos = []
    for video in response['items']:
        video_id = video['id']['videoId']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        if video_url not in st.session_state.get("videos", []):
            video_details = youtube.videos().list(part="snippet,contentDetails", id=video_id).execute()
            snippet = video_details['items'][0]['snippet']
            content_details = video_details['items'][0]['contentDetails']
            duration = content_details['duration']
            duration_seconds = isodate.parse_duration(duration).total_seconds()
            if duration_seconds <= max_duration * 60:
                data = {
                    "url": video_url,
                    "title": snippet.get("title"),
                    "description": snippet.get("description"),
                    "channel_title": snippet.get("channelTitle"),
                    "published_at": snippet.get("publishedAt"),
                    "duration": duration
                }
                videos.append(data)
        if len(videos) == max_results:
            break
    return videos
