import os
import speech_recognition as sr
import html
import asyncio
import openai
from elevenlabs import generate, play, set_api_key
import re

def extract_translation(text):
    match = re.search(r"'(.*)'", text)
    if match:
        return match.group(1)
    else:
        return text

# Set your OpenAI API key here
openai.api_key = 'Set your OpenAI API key here'

# Set your ElevenLabs API key here
set_api_key("Set your ElevenLabs API key here")

# Initialize recognizer
r = sr.Recognizer()

# Initialize microphone
m = sr.Microphone()

async def speak_text_async(text):
    # Generate audio from the text
    audio = generate(voice="Set your voice ID", model="eleven_multilingual_v1", text=text)
    play(audio)

async def listen_and_translate_speech_async(source):
    with source as s:
        r.energy_threshold = 5000
        print("Listening...")
        audio = r.listen(s, phrase_time_limit=10)
        try:
            recognized_text = r.recognize_google(audio, language='pt-BR')  # set language to Portuguese
            print("You said (in Portuguese):", recognized_text)

            response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                "role": "system",
                "content": "You are a helpful assistant who translates pt-BR to en-US. When given an pt-BR sentence, your task is to provide the en-US translation only, without any extra explanation or context. Yet, it should be sensible."
                },
                {
                    "role": "user",
                    "content": f"Translate this pt-BR sentence to en-US: '{recognized_text}'"
                }
            ]
        )

            translated_text = response['choices'][0]['message']['content']
            translated_text = extract_translation(translated_text)
            print("Translation in English:", translated_text)

            await speak_text_async(translated_text)

        except sr.UnknownValueError:
            print("Please speak up, I couldn't understand.")
        except sr.RequestError as e:
            print(f"Error occurred during speech recognition: {e}")

async def continuous_translation(source):
    try:
        while True:
            await listen_and_translate_speech_async(source)
    except KeyboardInterrupt:
        print("Terminated by You")

asyncio.run(continuous_translation(m))
