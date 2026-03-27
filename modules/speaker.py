# modules/speaker.py - Neural TTS for Jarvis (using Edge-TTS)
import os
import asyncio
import tempfile
import pygame
from edge_tts import Communicate
from config import VOICE_LANG, VOICE_SLOW

try:
    pygame.mixer.init()
    PYGAME_AVAILABLE = True
except:
    PYGAME_AVAILABLE = False

# Removed language detection, defaulting to English only

async def speak_async(text):
    """Neural speech out loud on PC."""
    try:
        if not PYGAME_AVAILABLE:
            print(f"🔊 Jarvis: {text} (Speaker OFF)")
            return

        print(f"🔊 Assistant is speaking...")
        # Select Neural Voice
        voice = "en-US-GuyNeural" # Natural Male Assistant
            
        audio_file = os.path.join(tempfile.gettempdir(), "jarvis_reply.mp3")
        
        # Generate neural audio
        communicate = Communicate(text, voice)
        await communicate.save(audio_file)

        # Play
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.1)

        os.remove(audio_file)
    except Exception as e:
        print(f"❌ Neural Speaker error: {e}")

def speak(text):
    """Wrapper for async speak."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(speak_async(text))

async def text_to_audio_file_async(text):
    """Convert text to neural audio file and return path."""
    try:
        # Select Neural Voice
        voice = "en-US-GuyNeural"
            
        tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        communicate = Communicate(text, voice)
        await communicate.save(tmp.name)
        return tmp.name
    except Exception as e:
        print(f"❌ Neural TTS file error: {e}")
        return None

def text_to_audio_file(text):
    """Sync wrapper for telegram bot."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(text_to_audio_file_async(text))
