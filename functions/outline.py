import streamlit as st
from openai import OpenAI


def generate_content_outline(project_component):
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    class_name = st.session_state["class_name"]
    scope = st.session_state["scope"]
    audience = st.session_state["audience"]
    knowledge_base = st.session_state["knowledge_base"]

    # Prepare the prompt for ChatGPT
    system_prompt = """
    You will be provided some general information regarding a potential class a teacher is working on.
    This includes the topic, intended scope of the lesson, and target demographic of students.
    Your task is to expand on the topic and scope of the lesson to help the teacher determine the topics, and order in which the topics should be presented to the students.
    This specifically means establishing the fundamental topics (items that must be covered), and the order in which those topics are presented to the student with relation to more constructive discussions.

    IMPORTANT: The teacher is looking for a natural progression of topics to cover over one single lesson, so the order of topics is crucial, and should not reference days or weeks.
    The students are trying to learn and understand the material, so provide annotations where necessary to explain why the topic's ___. Not just how the topic's ___.
    """
    prompt = f"""
#####
CLASS CONTEXT
#####
Class Name:
###
{class_name}
###

Ideal Scope of the Course:
###
{scope}
###

Intended Audience:
###
{audience}
###

Extra Reference Material:
###
{', '.join(knowledge_base) if knowledge_base else "None"}
###

Hypothetical Content Outline:
- Quick Introduction to {class_name}
    - Focus on why the student might care about the subject. This should be a very casual introduction that is no more than single point

    - Optional Introductory Topic 1
        - Leads to Fundamental Topic 1
        - This topic is like this because...
    - Fundamental Topic 1
    - Optional Advanced Topic 1
        - Builds from Fundamental Topic 1
    - Fundamental Topic 2
    - Optional Introductory Topic 2
        - Leads to Advanced Topic 2
    - Optional Advanced Topic 2
        - Builds from Optional Introductory Topic 2
    - ...
{"- Interactive Project: " if project_component else ""}
{"The project should be a hands-on activity that let the student apply the knowledge they have learned in the class." if project_component else ""}

YOU MUST RETURN A LIST OF TOPICS FOR THE LESSON THAT WOULD BE A NATURAL PROGRESSION FOR STUDENTS, ADDING CONTENT WHERE YOU SEE FIT.
The numbers or order of the topics above are not required, but the topics should be presented in a logical order for a single lesson.
DO NOT INCLUDE PLACEHOLDERS LIKE "Fundamental Topic 1" OR "Optional Advanced Topic 2" IN YOUR RESPONSE.
The associations between topics are provided as a guide for the relationships between topics, but the order should be determined by the importance of the topics to the overall understanding of the subject.
Only return the list of topics and annotations if relevant, no explanations are needed after.
Do not include "review" or "Q and A" sections in the outline. Instead include potential questions or review topics in the main outline with the subject. MAKE SURE to mark these as optional to the teacher.
"""

    # Call OpenAI to generate the content outline
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1500,
        )

        generated_outline = response.choices[0].message.content
        st.session_state["outline"] = generated_outline
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
