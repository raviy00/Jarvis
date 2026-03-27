# modules/transcriber.py - Voice to Text using Groq Whisper API
import os
from openai import OpenAI
from config import GROQ_API_KEY, GROQ_BASE_URL

client = OpenAI(api_key=GROQ_API_KEY, base_url=GROQ_BASE_URL)

def transcribe_audio(audio_path):
    """Transcribe audio file using Groq's Whisper API."""
    try:
        with open(audio_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=audio_file,
                response_format="text"
            )
        return transcription.strip()
    except Exception as e:
        print(f"❌ Transcription error: {e}")
        return None
