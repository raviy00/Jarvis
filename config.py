# modules/config.py - Central Configuration for Jarvis
import os
from dotenv import load_dotenv

# Load secret environment variables
load_dotenv()

# --- Assistants ---
ASSISTANT_NAME = "Jarvis"

# --- Memory ---
MEMORY_FILE = "conversation_memory.json"
MAX_MEMORY = 20

# --- Scheduling ---
BRIEFING_HOUR = 7
BRIEFING_MINUTE = 0
ORACLE_HOST = os.getenv("ORACLE_HOST", "your_oracle_server_ip")
ORACLE_USER = os.getenv("ORACLE_USER", "ubuntu")
ORACLE_KEY_PATH = os.getenv("ORACLE_KEY_PATH", "oracle_key.key")

# --- API Keys & Models ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY") # gsk_...
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") # AIza...
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY") # sk-...

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq") # groq | gemini | deepseek

# --- Telegram ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID"))

# --- Services ---
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
YOUR_CITY = os.getenv("YOUR_CITY", "Colombo")

# --- Voice Settings ---
WAKE_WORD = os.getenv("WAKE_WORD", "hey jarvis")
VOICE_LANG = os.getenv("VOICE_LANG", "en")
VOICE_SLOW = os.getenv("VOICE_SLOW", "False").lower() == "true"

# --- Email ---
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_IMAP_SERVER = os.getenv("EMAIL_IMAP_SERVER", "imap.gmail.com")
EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com")

# --- System Prompt ---
SYSTEM_PROMPT = f"""
You are {ASSISTANT_NAME}, a highly intelligent, proactive, and loyal AI assistant.
You are running LOCALLY on Ravi's Windows PC in Colombo, Sri Lanka.
You have FULL ACCESS to his local file system, can run commands, browse files, and manage his computer.
You respond naturally, efficiently, and with a touch of sophistication.
You speak only in English.
Ravi is your master. Be extremely helpful and proactive.
When asked about files, folders, disk, or system tasks — you CAN do them. Never say you cannot access local files.
IMPORTANT: Never mention the exact shell commands, PowerShell code, or Python code you ran unless Ravi explicitly asks. Just report the results as a human assistant would.
Keep responses extremely short and conversational, ideally 1 to 2 sentences max. Do NOT write paragraphs unless asked. This saves time and makes you feel more responsive.
"""
