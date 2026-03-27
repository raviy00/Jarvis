import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    # Manual key for test
    api_key = "AIzaSyBNrX3IgnnOIEnTBypE1QhCnVzOIfX5Qzc"

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash-latest")
try:
    response = model.generate_content("Hello")
    print(f"SUCCESS: {response.text}")
except Exception as e:
    print(f"FAILURE: {e}")
