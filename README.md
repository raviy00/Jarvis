# 🤖 Jarvis AI Assistant

Welcome to **Jarvis**, your personal, highly intelligent AI assistant! Jarvis is designed to be proactive, capable, and ready to help you manage your digital life. Whether you want to interact via voice locally, control things remotely through Telegram, or get daily briefings, Jarvis has you covered.

## ✨ Features

- **Multi-LLM Support:** Seamlessly switch between top-tier AI models including **Groq**, **Gemini**, and **DeepSeek** based on your preferences and needs.
- **📱 Telegram Integration:** Control Jarvis, ask questions, and receive proactive alerts directly from your Telegram app, wherever you are.
- **🎙️ Advanced Voice Features:** Talk to Jarvis locally! Features a custom wake word ("Hey Jarvis"), accurate speech-to-text, and natural neural voice responses.
- **🌤️ Daily Briefings & News:** Get morning updates on the weather for your city and the latest top news headlines.
- **⏰ Smart Reminders & Scheduling:** Set reminders and let Jarvis keep you on track.
- **🖥️ Web Dashboard:** A built-in web GUI (running on `http://localhost:5000`) for easy monitoring.

## 🛠️ Prerequisites

Before installing Jarvis, ensure you have the following software installed on your system:

- **Python 3.8+**
- **FFmpeg:** Required for processing audio and voice features.
  - *Windows:* Download from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) or install via winget: `winget install ffmpeg`
  - *macOS:* `brew install ffmpeg`
  - *Linux:* `sudo apt install ffmpeg`
- **Git** (for cloning the repository)

## 🚀 Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd jarvis-assistant
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Configuration & Environment Variables

Jarvis relies on a `.env` file to securely store your API keys and personal settings.

1. Create a file named `.env` in the root directory of the project.
2. Copy the following template into your `.env` file and fill in your keys:

```ini
# AI Providers (Get your free keys from their respective platforms)
GROQ_API_KEY=your_groq_api_key
GEMINI_API_KEY=your_gemini_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key

# Active LLM Pathway (Choose: groq, gemini, deepseek)
LLM_PROVIDER=groq

# Telegram Bot Token & Chat ID
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

# Services (Optional but recommended)
NEWS_API_KEY=your_news_api_key
WEATHER_API_KEY=your_openweather_api_key
YOUR_CITY=Colombo

# Personalized Settings
WAKE_WORD=hey jarvis
VOICE_LANG=en
VOICE_SLOW=False

# Email Credentials (Optional)
EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_app_specific_password
EMAIL_IMAP_SERVER=imap.gmail.com
EMAIL_SMTP_SERVER=smtp.gmail.com
```

## 🎮 Usage

Starting Jarvis is incredibly simple. Just run the main script:

```bash
python main.py
```

Once running, Jarvis will:
- Start the wake word listener for voice commands.
- Launch the Web Dashboard at `http://localhost:5000`.
- Connect to your Telegram Bot.

You can now say "Hey Jarvis" or send a message to your Telegram bot to start interacting!

## 🐳 Docker & Deployment

Jarvis is fully containerized and ready for remote deployment (e.g., on Oracle Cloud or any VPS).

### Using Docker Compose (Recommended)

1. Ensure Docker and Docker Compose are installed.
2. Make sure your `.env` file is fully configured.
3. Start Jarvis in the background:
   ```bash
   docker-compose up -d
   ```
4. To view logs:
   ```bash
   docker-compose logs -f
   ```
5. To stop the container:
   ```bash
   docker-compose down
   ```

### Deployment Script

For automated deployment to a remote server, a `deploy.sh` script is included. Ensure you have configured `ORACLE_HOST` and your SSH keys in `config.py` if you plan to use the custom deployment scripts for Oracle Cloud.

---
*Built with ❤️ to make your digital life easier.*
