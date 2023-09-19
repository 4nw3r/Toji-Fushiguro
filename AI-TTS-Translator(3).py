import os
import time
import speech_recognition as sr
from google.cloud import translate_v2 as translate
from google.cloud import texttospeech
import html
import asyncio
import playsound  # Needed to play the generated speech audio file

# Set your Google Cloud API key here
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'tts.json'

# Initialize recognizer, translator and TTS client
r = sr.Recognizer()
translate_client = translate.Client()
tts_client = texttospeech.TextToSpeechClient()

# Cache for translations
translation_cache = {}

# Determine concurrency limit for the TTS based on your needs
concurrent_limit = 15  # Adjust this based on your needs

# Semaphore to limit concurrent requests to the TTS
semaphore = asyncio.Semaphore(concurrent_limit)

async def speak_text_async(text):
    async with semaphore:
        # Check if text is in cache
        if text in translation_cache:
            audio = translation_cache[text]
        else:
            # Generate audio from the text
            synthesis_input = texttospeech.SynthesisInput(text=text)

            voice = texttospeech.VoiceSelectionParams(
                language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
            )

            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )

            response = tts_client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )

            # Save the audio to a file
            audio_file = f"{text}.mp3"
            with open(audio_file, "wb") as out:
                out.write(response.audio_content)

            # Store the file name in cache
            translation_cache[text] = audio_file
            audio = audio_file

        playsound.playsound(audio)
