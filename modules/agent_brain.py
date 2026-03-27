# modules/agent_brain.py - Action Layer for Jarvis
import os
from interpreter import interpreter
from config import GROQ_API_KEY, ASSISTANT_NAME

# Setup Interpreter for local task execution
interpreter.llm.model = "groq/llama-3.3-70b-versatile"
interpreter.llm.api_key = GROQ_API_KEY
interpreter.auto_run = True # Enable so he actually DOES the tasks
interpreter.offline = False
interpreter.safe_mode = False # Keep it off for basic file exploration

def execute_action(user_input):
    """
    Execute system-level tasks using Open Interpreter.
    """
    try:
        print(f"🛠️ {ASSISTANT_NAME} is looking into it: {user_input}")
        # Capture the output
        output = ""
        for chunk in interpreter.chat(user_input, display=True):
            if 'content' in chunk and chunk['type'] == 'message':
                output += chunk['content']
            elif 'content' in chunk and 'output' in chunk: # Code output
                output += f"\nResult: {chunk['content']}"

        return output.strip() if output else "✅ Done, Ravi."
        
    except Exception as e:
        print(f"❌ Action error: {e}")
        return f"I hit a snag while trying to act on your system: {e}"
