import os
import requests
import google.generativeai as genai

GEMINI_KEY = "AIzaSyBNrX3IgnnOIEnTBypE1QhCnVzOIfX5Qzc"
DEEPSEEK_KEY = "sk-a42dd3ba8430497e9069b3d48abcaab7"

def test_gemini():
    print("Testing Gemini...")
    try:
        genai.configure(api_key=GEMINI_KEY)
        # We'll use the most likely stable name instead of the 2.5/3.1 stuff if it's new
        model = genai.GenerativeModel("gemini-1.5-flash") # This is standard
        response = model.generate_content("Hi")
        print(f"✅ Gemini Response: {response.text}")
        return True
    except Exception as e:
        print(f"❌ Gemini Failed: {e}")
        return False

def test_deepseek():
    print("\nTesting DeepSeek...")
    try:
        url = "https://api.deepseek.com/chat/completions"
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "deepseek-chat", # This is the standard chat model
            "messages": [{"role": "user", "content": "Hi"}]
        }
        response = requests.post(url, headers=headers, json=data, timeout=10)
        if response.status_code == 200:
            print(f"✅ DeepSeek Response: {response.json()['choices'][0]['message']['content']}")
            return True
        else:
            print(f"❌ DeepSeek Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ DeepSeek Connection Error: {e}")
        return False

if __name__ == "__main__":
    test_gemini()
    test_deepseek()
