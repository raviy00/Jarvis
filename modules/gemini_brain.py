# modules/gemini_brain.py - Google Gemini Skill for Jarvis
import google.generativeai as genai
from config import GEMINI_API_KEY, SYSTEM_PROMPT

# Configure API
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("⚠️ GEMINI_API_KEY not set in .env")

# Stable model ID from the user account's available list
MODEL_ID = "models/gemini-2.0-flash" 

def think_gemini(user_input, history, mode="normal"):
    """
    Use Google Gemini for high-accuracy Sinhala and English responses.
    """
    if not GEMINI_API_KEY:
        return "❌ Gemini API key is missing."

    try:
        model = genai.GenerativeModel(MODEL_ID)
        
        system = SYSTEM_PROMPT
        if mode == "assignment":
            system += "\n[ASSIGNMENT MODE] Give detailed, academic, and structured Sinhala/English answers."
        
        context = f"SYSTEM: {system}\n"
        for msg in history:
            context += f"{'USER' if msg['role'] == 'user' else 'ASSISTANT'}: {msg['content']}\n"
        
        full_query = context + f"USER: {user_input}\nASSISTANT: "
        
        response = model.generate_content(full_query)
        return response.text.strip()
    except Exception as e:
        print(f"❌ Gemini Thinking error: {e}")
        raise e

def transcribe_gemini(audio_path):
    """Transcribe audio using Gemini's multi-modal capabilities."""
    if not GEMINI_API_KEY:
        return "Error: No Gemini API Key."
        
    try:
        model = genai.GenerativeModel(MODEL_ID)
        
        with open(audio_path, "rb") as f:
            audio_data = f.read()
            
        import mimetypes
        mime_type, _ = mimetypes.guess_type(audio_path)
        if not mime_type:
            mime_type = "audio/ogg" 
            
        response = model.generate_content([
            "Transcribe exactly what is said in this audio. If you can't hear anything, return '[No speech detected]'. Use English or Sinhala script.",
            {"mime_type": mime_type, "data": audio_data}
        ])
        
        return response.text.strip()
    except Exception as e:
        print(f"❌ Gemini Transcription error: {e}")
        return f"Error: {e}"
