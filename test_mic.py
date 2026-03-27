import speech_recognition as sr
import os
import pygame
from modules.speaker import speak

def test_mic():
    r = sr.Recognizer()
    mic = sr.Microphone()
    print("🎤 Adjusting for ambient noise... please be quiet.")
    with mic as source:
        r.adjust_for_ambient_noise(source, duration=1)
    
    print("🎤 Please say 'Hello Jarvis' now!")
    with mic as source:
        try:
            audio = r.listen(source, timeout=5)
            text = r.recognize_google(audio)
            print(f"✅ Mic Heard: {text}")
            speak(f"I heard you say: {text}. Your microphone is working perfectly, Ravi.")
        except Exception as e:
            print(f"❌ Mic Error: {e}")

if __name__ == "__main__":
    test_mic()
