# modules/voice_listener.py - Robust Always-on Voice Listener for Jarvis
import speech_recognition as sr
import os
import tempfile
import threading
import time
from modules.transcriber import transcribe_audio
from modules.brain import think, detect_mode
from modules.speaker import speak
from modules.memory import load_memory, add_message
from config import WAKE_WORD, ASSISTANT_NAME

def listen_loop():
    """Main loop for listening to the wake word and processing commands."""
    r = sr.Recognizer()
    mic = sr.Microphone()
    
    # Sensitivity adjustments
    r.dynamic_energy_threshold = True
    r.energy_threshold = 300 # Start baseline
    
    # Sensitivity adjustments
    r.dynamic_energy_threshold = True
    r.energy_threshold = 150 # Even more sensitive for quiet rooms
    r.pause_threshold = 0.4 # Faster cutoff after user stops speaking
    
    print(f"🎙️ Jarvis Listener: Active (Wake word: '{WAKE_WORD}')")
    
    with mic as source:
        print("🎤 Adjusting for background noise (be quiet for 1.5s)...")
        r.adjust_for_ambient_noise(source, duration=1.5)
        
    while True:
        try:
            with mic as source:
                print("👂 Listening...") # Clearer status
                audio = r.listen(source, timeout=None, phrase_time_limit=3)
                
            # Quick check for wake word
            try:
                text = r.recognize_google(audio).lower()
                print(f"Heard [Local Mic]: {text}")
                
                # Check for variations of the wake word
                wake_variations = [WAKE_WORD, 'jarvis', 'jars', 'service', 'travis']
                if any(w in text for w in wake_variations):
                    print(f"✨ Wake word detected!")
                    speak("Yes Ravi, I'm here.")
                    
                    # Now listen for the actual command
                    with mic as source:
                        audio_cmd = r.listen(source, timeout=5, phrase_time_limit=10)
                    
                    # Save audio to temp file
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                        f.write(audio_cmd.get_wav_data())
                        cmd_path = f.name
                    
                    # Transcribe using Groq (SOTA)
                    command = transcribe_audio(cmd_path)
                    os.unlink(cmd_path)
                    
                    if command:
                        print(f"🎯 Command: {command}")
                        history = load_memory()
                        reply = think(command, history)
                        
                        add_message(history, "user", command)
                        add_message(history, "assistant", reply)
                        
                        speak(reply)

                        # Push to web dashboard in real-time
                        try:
                            from modules.web_gui import push_event
                            push_event("user", command)
                            push_event("jarvis", reply)
                        except Exception:
                            pass
                            
            except sr.UnknownValueError:
                pass # Silently ignore unidentifiable noises
            except sr.RequestError as e:
                print(f"⚠️ Speech API network error: {e}")
                time.sleep(1)
                
        except Exception as e:
            if "Remote end closed connection" in str(e):
                # This is a common transient network error - just retry quickly
                time.sleep(0.2)
            else:
                print(f"⚠️ Listener restart due to error: {e}")
                time.sleep(1) # Wait and continue

def start_listener():
    """Start the listener in a background thread."""
    t = threading.Thread(target=listen_loop, daemon=True)
    t.start()
    return t
