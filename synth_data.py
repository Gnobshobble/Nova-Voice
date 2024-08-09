import openai
from pathlib import Path
from openai import OpenAI
import os
from pydub import AudioSegment
from scipy.io import wavfile
from tempfile import mktemp
import sys
sys.path.append('/path/to/ffmpeg')


client = OpenAI()

# Function to generate text using OpenAI's GPT model
def get_text(index):
    response = client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {"role": "user", "content": "Generate a couple random sentences"}
        ]
    )
    with open(f'/Users/rishabh/NovaVoice/Nova-Voice/data/text/output_{index}.txt', 'x') as f:
        f.write(response.choices[0].message.content)
    return response.choices[0].message.content

# Function to generate audio from text using OpenAI's TTS model
def get_audio(text, index):
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text
    )
    response.stream_to_file(f'/Users/rishabh/NovaVoice/Nova-Voice/data/audio/output_{index}.mp3')

# Function to save the dictionary to a file
def save_dictionary_to_file(dictionary, file_path):
    with open(file_path, 'w') as f:
        for text, audio_data in dictionary.items():
            f.write(f"Text: {text}\nAudio Data: {audio_data}\n\n")

# Convert audio to mel spectograms
def convert_audio(index):
    # TODO
    mp3_audio = AudioSegment.from_mp3(f'/Users/rishabh/NovaVoice/Nova-Voice/data/audio/output_{index}.mp3')  # read mp3
    mp3_audio.export(f'/Users/rishabh/NovaVoice/Nova-Voice/data/mel/output_{index}.wav', format="wav")  # convert to wav
    
# Returns number of characters in the longest text file
def getLongestData(file_path):
    # TODO
    return 0

# Main script
dictionary = {}

for i in range(50):
    # text = get_text(i)
    # get_audio(text, i)
    convert_audio(i)
    # dictionary[text] = audio_data

# Save the dictionary to a file
# save_dictionary_to_file(dictionary, 'text_to_audio_dictionary.txt')

# Save example audio file
# speech_file_path = Path(__file__).parent / "speech.mp3"
# with open(speech_file_path, 'wb') as audio_file:
#     audio_file.write(dictionary[list(dictionary.keys())[0]])