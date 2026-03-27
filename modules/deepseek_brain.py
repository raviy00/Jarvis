# modules/deepseek_brain.py - DeepSeek Chat Integration
import requests
import json
from config import DEEPSEEK_API_KEY, SYSTEM_PROMPT

def think_deepseek(user_input, history, mode="normal"):
    """
    Use DeepSeek Chat (v3) for high-performance reasoning.
    """
    if not DEEPSEEK_API_KEY:
        return "❌ DeepSeek API key is missing."

    try:
        url = "https://api.deepseek.com/chat/completions"
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Build messages
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for msg in history:
            messages.append(msg)
        messages.append({"role": "user", "content": user_input})
        
        data = {
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1500
        }
        
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=20)
        if response.status_code == 200:
            res_json = response.json()
            return res_json['choices'][0]['message']['content'].strip()
        else:
            print(f"❌ DeepSeek Error: {response.status_code} - {response.text}")
            raise Exception(f"DeepSeek returned {response.status_code}")
            
    except Exception as e:
        print(f"❌ DeepSeek Connection Fail: {e}")
        raise e
