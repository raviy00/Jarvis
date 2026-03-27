# modules/memory.py - Conversation Memory

import json
import os
from config import MEMORY_FILE, MAX_MEMORY


def load_memory():
    """Load conversation history from file."""
    if not os.path.exists(MEMORY_FILE):
        dirn = os.path.dirname(MEMORY_FILE)
        if dirn:
            os.makedirs(dirn, exist_ok=True)
        return []
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_memory(messages):
    """Save conversation history to file."""
    trimmed = messages[-MAX_MEMORY:]
    dirn = os.path.dirname(MEMORY_FILE)
    if dirn:
        os.makedirs(dirn, exist_ok=True)
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(trimmed, f, ensure_ascii=False, indent=2)


def add_message(messages, role, content):
    """Add a message to history and save."""
    messages.append({"role": role, "content": content})
    save_memory(messages)
    return messages


def clear_memory():
    """Clear all conversation history."""
    if os.path.exists(MEMORY_FILE):
        os.remove(MEMORY_FILE)
    print("🧹 Memory cleared.")
