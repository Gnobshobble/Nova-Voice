import streamlit as st
from openai import OpenAI
from prompts.student import student_instructions
from prompts.teacher import class_resources, teacher_instructions


class TeacherSimulator:
    def __init__(self):
        # OpenAI Client
        self.client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        # Prompts
        self.instructions = teacher_instructions
        self.class_resources = class_resources

        # Course Materials
        self.class_name = st.session_state.get("class_name", "")
        self.scope = st.session_state.get("scope", "")
        self.audience = st.session_state.get("audience", "")
        self.knowledge_base = st.session_state.get("knowledge_base", [])
        self.outline = st.session_state.get("outline", "")
        self.videos = st.session_state.get("videos", {})
        self.video_titles = [video["title"] for video in self.videos]
        self.video_urls = [video["url"] for video in self.videos]
        self.images = st.session_state.get("images", {})
        self.image_titles = [image["title"] for image in self.images]
        self.image_urls = [image["url"] for image in self.images]
        self.associations = st.session_state.get("associations", [])

        # Prepare the system prompt
        self.format_class_resources()
        self.system_prompt = self.instructions + "\n" + self.class_resources

    def format_class_resources(self):
        # Fills in the values in Class Resources from the session state
        # Returns a formatted string
        videos = ', '.join([f"{title}: {url}" for title, url in zip(self.video_titles, self.video_urls)]) if self.videos else 'None'
        images = ', '.join([f"{title}: {url}" for title, url in zip(self.image_titles, self.image_urls)]) if self.images else 'None'
        associations = ", ".join(self.associations) if self.associations else "None"
        self.class_resources = self.class_resources.format(
            class_name=self.class_name,
            scope=self.scope,
            audience=self.audience,
            outline=self.outline,
            videos=videos,
            images=images,
            connections=associations,
        )

    def generate_response(self, last_messages):
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=last_messages,
            # {"role": "system", "content": "You are Nova, an AI teaching assistant."},
            # {"role": "user", "content": prompt}
        )

        return response.choices[0].message.content


class StudentSimulator:
    def __init__(self):
        # OpenAI Client
        self.client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

        # Prompts
        self.instructions = student_instructions

    def generate_response(self, last_messages):
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=last_messages,
            # {"role": "system", "content": "You are Nova, an AI teaching assistant."},
            # {"role": "user", "content": prompt}
        )

        return response.choices[0].message.content


class ConversationSimulator:
    def __init__(self):
        self.teacher = TeacherSimulator()
        self.student = StudentSimulator()
        self.message_log = []

        self.filtered_student_log = []
        self.filtered_teacher_log = []

    def simulate_conversation(self):
        # Preface the conversation with instructions
        self.filtered_teacher_log.append(
            {"role": "system", "content": self.teacher.system_prompt}
        )
        self.filtered_student_log.append(
            {"role": "system", "content": self.student.instructions}
        )

        # Starting the conversation
        # instructions
        self.filtered_teacher_log.append(
            {
                "role": "system",
                "content": "Open with a greeting to the student. Introduce what you will be teaching today. Try to get them excited about the topic.",
            }
        )
        # response generated
        teacher_message = self.teacher.generate_response(self.filtered_teacher_log)
        # log the response
        self.mass_log(
            [self.filtered_teacher_log, self.message_log],
            {"role": "assistant", "content": teacher_message},
        )
        self.mass_log(
            [self.filtered_student_log], {"role": "user", "content": teacher_message}
        )

        self.filtered_student_log.append(
            {
                "role": "system",
                "content": "React as you (a student) normally would to the previous message. Remember your original instructions.",
            }
        )
        student_message = self.student.generate_response(self.filtered_student_log)
        self.mass_log(
            [self.filtered_teacher_log, self.message_log],
            {"role": "user", "content": student_message},
        )
        self.mass_log(
            [self.filtered_student_log],
            {"role": "assistant", "content": student_message},
        )

        while True:
            # Teacher sends a message
            self.filtered_teacher_log.append(
                {
                    "role": "system",
                    "content": "###ORIGINAL INSTRUCTIONS:\n"
                    + self.teacher.system_prompt,
                }
            )
            self.filtered_teacher_log.append(
                {
                    "role": "system",
                    "content": "Based on the student's last message and the context of the conversation, provide a response that continues the conversation. Remember your original instructions.",
                }
            )
            teacher_message = self.teacher.generate_response(self.filtered_teacher_log)
            self.mass_log(
                [self.filtered_teacher_log, self.message_log],
                {"role": "assistant", "content": teacher_message},
            )
            self.mass_log(
                [self.filtered_student_log],
                {"role": "user", "content": teacher_message},
            )

            # Student sends a message
            self.filtered_student_log.append(
                {
                    "role": "system",
                    "content": "###ORIGINAL INSTRUCTIONS:\n"
                    + self.student.instructions,
                }
            )
            self.filtered_student_log.append(
                {
                    "role": "system",
                    "content": "React as you (a student) normally would to the previous message. Remember your original instructions.",
                }
            )
            student_message = self.student.generate_response(self.filtered_student_log)
            self.mass_log(
                [self.filtered_teacher_log, self.message_log],
                {"role": "user", "content": student_message},
            )
            self.mass_log(
                [self.filtered_student_log],
                {"role": "assistant", "content": student_message},
            )

            # Check if the conversation is over
            if "So long and thanks for all the fish".lower() in student_message.lower():
                break
        # return self.message_log[:-2]
        return self.format_conversation()

    def clean_message(self, message):
        # Replace escape characters with their corresponding symbols
        message = message.replace("\\n", "\n").replace("\\t", "\t").replace("\\r", "\r")

        # Remove any characters that are not part of Markdown
        # Allow printable ASCII characters, including common punctuation
        # message = re.sub(r'[^a-zA-Z0-9\s\.,!?\':;\"\-\(\)_\[\]\{\}]', '', message)

        return message

    def format_conversation(self):
        formatted_conversation = []

        for entry in self.message_log:
            role = entry["role"]
            content = self.clean_message(entry["content"])

            if role == "assistant":
                formatted_conversation.append(f"**Nova**: {content}")
            elif role == "user":
                formatted_conversation.append(f"**Student**: {content}")

        return "\n".join(formatted_conversation)

    def mass_log(self, lists, message):
        # for each list in lists, log the message
        for l in lists:
            l.append(message)
