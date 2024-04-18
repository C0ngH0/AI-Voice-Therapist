import sounddevice as sd
import soundfile as sf
import numpy as np
import openai
import wave
import os
import requests
import re
from colorama import Fore, Style, init
import datetime
import base64
from pydub import AudioSegment
from pydub.playback import play
import webrtcvad
import pyaudio
init()

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()
backup_filename = 'chatbot1_backup.txt'
original_filename = 'chatbot1.txt'

# Ensure there's a backup of the original file content
if not os.path.exists(backup_filename):
    with open(original_filename, 'r') as original, open(backup_filename, 'w') as backup:
        backup.write(original.read())

template_file_path = 'chatbot1.txt'

# Path to the personalized file (optional, only if you need to save the personalized message)
personalized_file_path = 'chatbot2.txt'

user_name = input("Please enter your name: ")


with open(template_file_path, 'r') as file:
    template_content = file.read()

personalized_content = template_content.replace("[name]", user_name)

# Optionally save to a new file or simply print
with open(personalized_file_path, 'w') as file:
    file.write(personalized_content)

    

api_key = open_file('openaiapikey2.txt')
elapikey = open_file('elabapikey.txt')

conversation1 = []  
chatbot1 = open_file('chatbot2.txt')



def chatgpt(api_key, conversation, chatbot, user_input, temperature=0.9, frequency_penalty=0.2, presence_penalty=0):
    openai.api_key = api_key
    conversation.append({"role": "user","content": user_input})
    messages_input = conversation.copy()
    prompt = [{"role": "system", "content": chatbot}]
    messages_input.insert(0, prompt[0])
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        temperature=temperature,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        messages=messages_input)
    chat_response = completion['choices'][0]['message']['content']
    conversation.append({"role": "assistant", "content": chat_response})
    return chat_response

def text_to_speech(text, voice_id, api_key):
    url = f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}'
    headers = {
        'Accept': 'audio/mpeg',
        'xi-api-key': api_key,
        'Content-Type': 'application/json'
    }
    data = {
        'text': text,
        'model_id': 'eleven_monolingual_v1',
        'voice_settings': {
            'stability': 0.6,
            'similarity_boost': 0.85
        }
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        with open('output.mp3', 'wb') as f:
            f.write(response.content)
        audio = AudioSegment.from_mp3('output.mp3')
        play(audio)
    else:
        print('Error:', response.text)

def print_colored(agent, text):
    agent_colors = {
        "Safe Space:": Fore.YELLOW,
    }
    color = agent_colors.get(agent, "")
    print(color + f"{agent}: {text}" + Style.RESET_ALL, end="")

while True:
    # Prompt the user to choose an accent
    accent_choice = input("Please choose an accent (American, Australian, British): ")
    
    # Normalize the input to lowercase to make the comparison case-insensitive
    accent_choice = accent_choice.lower()
    
    # Use an if-else statement to respond based on the choice
    if accent_choice == "american":
        voice_id1 = 'jsCqWAovK2LkecY7zXl4'
        print("You've chosen the American accent.")
        break  # Exit the loop
    elif accent_choice == "australian":
        voice_id1 = 'ZQe5CZNOzWyzPSCn5a3c'
        print("You've chosen the Australian accent.")
        break  # Exit the loop
    elif accent_choice == "british":
        voice_id1 = 'ThT5KcBeYPX3keUQqHPh'
        print("You've chosen the British accent.")
        break  # Exit the loop
    else:
        print("Invalid choice. Please choose American, Australian, or British.")


def record_with_vad_and_transcribe(aggressiveness=3, fs=16000, frame_duration=30, padding_duration=1000):
    vad = webrtcvad.Vad(aggressiveness)
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16, channels=1, rate=fs, input=True, frames_per_buffer=fs * frame_duration // 1000)

    print('Please start speaking.')
    frames = []
    num_silent_frames = 0
    num_padding_frames = padding_duration // frame_duration
    speech_detected = False

    while True:
        frame = stream.read(fs * frame_duration // 1000, exception_on_overflow=False)
        is_speech = vad.is_speech(frame, fs)

        if speech_detected:
            frames.append(frame)
            num_silent_frames = 0 if is_speech else num_silent_frames + 1
            if num_silent_frames > num_padding_frames:
                break  # Stop recording after `padding_duration` ms of silence
        elif is_speech:
            speech_detected = True
            print("Recording...")
            frames.append(frame)  # Start recording after detecting speech

    stream.stop_stream()
    stream.close()
    audio.terminate()

    print('Recording stopped, processing...')

    # Save the recorded frames as a WAV file
    filename = 'myrecording.wav'
    wf = wave.open(filename, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()

    # Transcription using your existing method
    with open(filename, "rb") as file:
        openai.api_key = api_key
        result = openai.Audio.transcribe("whisper-1", file)
    transcription = result['text']
    return transcription


while True:
    user_message = record_with_vad_and_transcribe()
    response = chatgpt(api_key, conversation1, chatbot1, user_message)
    print_colored("Safe Space:", f"{response}\n\n")
    user_message_without_generate_image = re.sub(r'(Response:|Narration:|Image: generate_image:.*|)', '', response).strip()
    text_to_speech(user_message_without_generate_image, voice_id1, elapikey)

