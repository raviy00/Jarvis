# modules/brain.py - Multi-Brain Integration for Jarvis (All Free Models)
import os
from config import SYSTEM_PROMPT, LLM_PROVIDER, GROQ_API_KEY, GEMINI_API_KEY, DEEPSEEK_API_KEY
from openai import OpenAI

# --- Clients ---
groq_client = None
if GROQ_API_KEY:
    groq_client = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")

deepseek_client = None
if DEEPSEEK_API_KEY:
    deepseek_client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com/chat/completions")

def _is_corrupted(text):
    """Check if a response is a repetition loop (especially ', .')"""
    if not text:
        return False
    # Check for the dreaded ', .' pattern specifically
    if text.count(', .') > 4 or text.count('. ,') > 4:
        return True
    # General check for any character or small phrase repeating too much
    for length in range(1, 15):
        for i in range(len(text) - length * 4):
            chunk = text[i:i+length]
            if not chunk.strip(): continue
            if text[i+length:i+length*2] == chunk and \
               text[i+length*2:i+length*3] == chunk and \
               text[i+length*3:i+length*4] == chunk:
                return True
    return False

def _clean_response(text):
    """Filter out corrupted LLM output."""
    if not text:
        return "I'm here, Ravi. How can I help?"
    if _is_corrupted(text):
        print("⚠️ Detected corrupted repetition loop — blocking response")
        return "I apologize, Ravi. I had a processing glitch. Could you please repeat your question?"
    return text

def think(user_input, conversation_history, mode="normal"):
    """
    Tries all available free models in order of priority (Groq -> Gemini -> DeepSeek).
    """
    
    # Mode detection
    mode = detect_mode(user_input)
    
    # 0. NATIVE APP LAUNCHER (Intercept "open X")
    u_lower = user_input.lower().strip()
    if u_lower.startswith("open "):
        app_name = user_input[5:].strip()
        try:
            from modules.local_apps import launch_app_on_pc
            _, launch_msg = launch_app_on_pc(app_name)
            return launch_msg
        except Exception as e:
            return f"I had an issue launching the app: {e}"

    # Sanitize history — remove any corrupted old messages
    clean_history = [msg for msg in conversation_history if not _is_corrupted(msg.get('content', ''))]

    # 0. Action/Agent — Route to Interpreter for system tasks
    action_words = [
        "find file", "open file", "summarize my", "check my", "run a command",
        "make a", "desktop", "scripts", "local disk", "disk c", "disk d",
        "list files", "list folder", "show files", "show folder", "my files",
        "my folders", "my documents", "what files", "what's on", "access my",
        "browse", "search my computer", "system info", "storage", "how much space",
    ]
    if any(w in user_input.lower() for w in action_words):
        try:
            from modules.agent_brain import execute_action
            return execute_action(user_input)
        except Exception as e:
            print(f"⚠️ Action brain failed: {e}")

    # 1. Groq (Primary — fast 8B for chat, 70B for complex)
    if groq_client:
        try:
            # Use fast model for simple chat, heavy model for assignments/complex
            if mode in ("assignment", "search"):
                model_name = "llama-3.3-70b-versatile"
                max_tok = 800
                print("🧠 Brain: Groq (Llama 3.3 70B — Deep Mode)...")
            else:
                model_name = "llama-3.1-8b-instant"
                max_tok = 300
                print("🧠 Brain: Groq (Llama 3.1 8B — Speed Mode)...")
            
            messages = [{"role": "system", "content": SYSTEM_PROMPT}] + clean_history[-6:] + [{"role": "user", "content": user_input}]
            response = groq_client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=0.7,
                max_tokens=max_tok,
                frequency_penalty=1.2,
            )
            return _clean_response(response.choices[0].message.content.strip())
        except Exception as e:
            print(f"⚠️ Groq failed: {e}")

    # 2. Gemini (Backup 1)
    if GEMINI_API_KEY:
        try:
            print("🧠 Brain: Trying Gemini 2.0 Flash...")
            from modules.gemini_brain import think_gemini
            return think_gemini(user_input, conversation_history, mode)
        except Exception as e:
            print(f"⚠️ Gemini failed: {e}")

    # 3. DeepSeek (Backup 2)
    if DEEPSEEK_API_KEY:
        try:
            print("🧠 Brain: Trying DeepSeek V3...")
            from modules.deepseek_brain import think_deepseek
            return think_deepseek(user_input, conversation_history, mode)
        except Exception as e:
            print(f"⚠️ DeepSeek failed: {e}")

    return "❌ All AI pathways are currently unavailable, Ravi. Please check your API keys or internet connection."

def detect_mode(user_input):
    """Detect what mode to use based on user input."""
    text = user_input.lower()
    if any(w in text for w in ["assignment", "essay", "report", "write about", "explain in detail", "uni", "university", "homework"]):
        return "assignment"
    elif any(w in text for w in ["search", "find", "look up", "news"]):
        return "search"
    elif any(w in text for w in ["play", "song", "music", "audio", "listen to", "stop", "pause", "shut up", "quiet"]):
        return "media"
    else:
        return "normal"
