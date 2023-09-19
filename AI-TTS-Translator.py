import os
import time
import speech_recognition as sr
from google.cloud import translate_v2 as translate
import html
import asyncio
from elevenlabs import generate, play, set_api_key

# Set your Google Cloud API key here
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'Location of the credential .json file'

# Set your ElevenLabs API key here
set_api_key("Set your ElevenLabs API key here")

# Initialize recognizer and translator
r = sr.Recognizer()
translate_client = translate.Client()

# Cache for translations
translation_cache = {}

# Determine concurrency limit for ElevenLabs based on your tier
concurrent_limit = 15  # Adjust this based on your ElevenLabs tier

# Semaphore to limit concurrent requests to ElevenLabs
semaphore = asyncio.Semaphore(concurrent_limit)

async def speak_text_async(text):
    async with semaphore:
        # Check if text is in cache
        if text in translation_cache:
            audio = translation_cache[text]
        else:
            # Generate audio from the text
            audio = generate(voice="Set Your ElevenLabs Voice ID", model="eleven_multilingual_v1", text=text)
            # Store audio in cache
            translation_cache[text] = audio
        play(audio)

async def listen_and_translate_speech_async():
    with sr.Microphone() as source:
        r.energy_threshold = 5000
        print("Listening...")
        audio = r.listen(source, phrase_time_limit=10)
        try:
            # Set language to English
            recognized_text = r.recognize_google(audio, language='pt-BR')  
            print("You said (in English):", recognized_text)

            translation = translate_client.translate(recognized_text, target_language='en')
            translated_text = html.unescape(translation['translatedText'])
            print("Translation in Portuguese:", translated_text)

            await speak_text_async(translated_text)

        except sr.UnknownValueError:
            print("Please speak up, I couldn't understand.")
        except sr.RequestError as e:
            print(f"Error occurred during speech recognition: {e}")

async def continuous_translation():
    try:
        while True:
            await listen_and_translate_speech_async()
    except KeyboardInterrupt:
        print("Terminated by You")

asyncio.run(continuous_translation())
