# modules/telegram_bot.py - Telegram Interface for Jarvis

import os
import asyncio
import tempfile
from telegram import Update, Bot
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
from modules.brain import think, detect_mode
from modules.memory import load_memory, add_message
from modules.speaker import text_to_audio_file
from modules.search import web_search
from modules.documents import save_as_docx
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, ASSISTANT_NAME


def is_authorized(update: Update) -> bool:
    """Only respond to your own Telegram account."""
    if update.effective_user.id != TELEGRAM_CHAT_ID:
        print(f"⚠️ Unauthorized access attempt from ID: {update.effective_user.id} ({update.effective_user.first_name})")
        return False
    return True


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    await update.message.reply_text(
        f"👋 Hey Ravi! I'm {ASSISTANT_NAME}, your personal AI assistant.\n\n"
        "You can:\n"
        "• Send me text messages\n"
        "• Send voice notes\n"
        "• Ask me anything\n"
        "• Say 'assignment: [topic]' for uni work\n"
        "• Say 'search: [query]' to search the web\n"
        "• Say 'save doc' to save last reply as Word file\n"
        "• Say 'clear memory' to reset conversation\n\n"
        "Ready when you are! 🚀"
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return

    user_input = update.message.text.strip()
    print(f"📩 Telegram from {update.effective_user.first_name}: {user_input}")
    await update.message.chat.send_action("typing")

    # Load memory
    history = load_memory()

    # Handle special commands
    if user_input.lower() == "clear memory":
        from modules.memory import clear_memory
        clear_memory()
        await update.message.reply_text("🧹 Memory cleared! Starting fresh.")
        return

    if user_input.lower().startswith("search:"):
        query = user_input[7:].strip()
        from modules.search import web_search
        result = web_search(query)
        await update.message.reply_text(f"🔍 *Search Results:*\n\n{result}", parse_mode="Markdown")
        return

    if user_input.lower().startswith("weather"):
        from modules.weather import get_weather
        city = None
        if "in " in user_input.lower():
            city = user_input.lower().split("in ")[-1].strip().title()
        result = get_weather(city)
        await update.message.reply_text(result)
        return

    if user_input.lower() == "save doc":
        if history:
            last_reply = history[-1]["content"] if history else "Nothing to save."
            from modules.documents import save_as_docx
            path = save_as_docx(last_reply)
            if path:
                await update.message.reply_document(document=open(path, "rb"), filename="jarvis_output.docx")
            else:
                await update.message.reply_text("❌ Failed to save document.")
        return

    if user_input.lower().startswith("wiki:"):
        from modules.wikipedia_skill import search_wiki
        res = search_wiki(user_input[5:].strip())
        await update.message.reply_text(res, parse_mode="Markdown")
        return

    if any(w in user_input.lower() for w in ["quote", "joke", "inspire me"]):
        from modules.quotes import get_random_quote, get_joke
        if "joke" in user_input.lower():
            res = get_joke()
        else:
            res = get_random_quote()
        await update.message.reply_text(res, parse_mode="Markdown")
        return

    if any(w in user_input.lower() for w in ["nasa", "space photo"]):
        from modules.nasa import get_nasa_image
        res = get_nasa_image()
        await update.message.reply_text(res, parse_mode="Markdown")
        return

    if user_input.lower().startswith("email:"):
        from modules.emails import check_emails
        res = check_emails()
        await update.message.reply_text(res, parse_mode="Markdown")
        return

    if user_input.lower().startswith("whatsapp:"):
        # Format: whatsapp: [number] [message]
        parts = user_input[10:].split(" ", 1)
        if len(parts) == 2:
            num, msg = parts
            from modules.phone import send_whatsapp
            res = send_whatsapp(num, msg)
            await update.message.reply_text(res)
        else:
            await update.message.reply_text("❌ Format: `whatsapp: [phone_number] [message]`")
        return

    if user_input.lower().startswith("open app:"):
        # Using package name or alias
        pkg = user_input[10:].strip()
        from modules.phone import open_app
        res = open_app(pkg)
        await update.message.reply_text(f"📱 Opening app: {pkg}")
        return

    # Detect mode
    mode = detect_mode(user_input)

    # Special handling for media
    if mode == "media":
        from modules.media import handle_music_request
        reply = handle_music_request(user_input)
        await update.message.reply_text(reply)
        return

    # Get reply from LLM
    reply = think(user_input, history, mode=mode)

    # Save to memory
    add_message(history, "user", user_input)
    add_message(history, "assistant", reply)

    # Send text reply ONLY (streamlined)
    if len(reply) > 4000:
        chunks = [reply[i:i+4000] for i in range(0, len(reply), 4000)]
        for chunk in chunks:
            await update.message.reply_text(chunk)
    else:
        await update.message.reply_text(reply)

    # If assignment mode, offer to save as doc
    if mode == "assignment":
        await update.message.reply_text("💾 Reply 'save doc' to save this as a Word document.")


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return

    await update.message.chat.send_action("typing")

    # Download voice note
    voice_file = await update.message.voice.get_file()
    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as f:
        await voice_file.download_to_drive(f.name)
        voice_path = f.name

    # Transcribe with Groq Whisper
    try:
        from openai import OpenAI
        from config import GROQ_API_KEY
        
        audio_client = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")
        
        with open(voice_path, "rb") as audio_file:
            transcription = audio_client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=audio_file,
                response_format="text"
            )
        user_input = transcription.strip()
    except Exception as e:
        print(f"❌ Groq transcription error: {e}")
        user_input = "Error transcribing voice note."
    
    os.unlink(voice_path)

    if "[No speech detected]" in user_input:
        await update.message.reply_text("🤔 I couldn't hear any speech, Ravi. Could you try again?")
        return

    await update.message.reply_text(f"🎙️ You said: _{user_input}_", parse_mode="Markdown")

    # Get reply
    history = load_memory()
    mode = detect_mode(user_input)
    
    # Special handling for media
    if mode == "media":
        from modules.media import handle_music_request
        reply = handle_music_request(user_input)
        # For media, usually text confirmation is better or just play?
        # User said "voice command -> voice response", so we keep it.
        audio_path = text_to_audio_file(reply)
        if audio_path:
            with open(audio_path, "rb") as audio:
                await update.message.reply_voice(voice=audio)
        return

    reply = think(user_input, history, mode=mode)

    # Save memory
    add_message(history, "user", user_input)
    add_message(history, "assistant", reply)

    # Send voice note reply ONLY (streamlined)
    audio_path = text_to_audio_file(reply)
    if audio_path:
        with open(audio_path, "rb") as audio:
            await update.message.reply_voice(voice=audio)
        if os.path.exists(audio_path):
            os.unlink(audio_path)


async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle location updates (static and live)."""
    if not is_authorized(update):
        return
        
    location = update.effective_message.location
    lat = location.latitude
    lon = location.longitude
    
    from modules.location import update_from_telegram
    update_from_telegram(lat, lon)
    
    # Optional: confirm to user if it's the first static location
    if not update.edited_message:
        await update.effective_message.reply_text("📍 Real-time location updated for your session, Ravi.")

async def send_message(text: str):
    """Send a proactive message to Ravi (for alerts, briefings etc)."""
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text)


def run_bot():
    """Start the Telegram bot."""
    print(f"🤖 {ASSISTANT_NAME} Telegram bot starting...")
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).read_timeout(30).connect_timeout(30).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    app.add_handler(MessageHandler(filters.UpdateType.EDITED_MESSAGE & filters.LOCATION, handle_location))

    print(f"✅ {ASSISTANT_NAME} is live on Telegram!")
    app.run_polling(drop_pending_updates=False, timeout=60, poll_interval=1.0)
