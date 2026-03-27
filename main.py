# main.py - Jarvis Entry Point

import asyncio
import threading
from modules.telegram_bot import run_bot, send_message
from modules.scheduler import briefing_loop, reminder_loop
from modules.server_monitor import monitor_loop
from config import ASSISTANT_NAME, ORACLE_HOST


def print_banner():
    print("""
    ╔══════════════════════════════════════════╗
    ║                                          ║
    ║         🤖 J A R V I S                  ║
    ║      Personal AI Assistant               ║
    ║      Powered by Groq + Neural Voice      ║
    ║                                          ║
    ╚══════════════════════════════════════════╝
    """)


async def run_background_tasks():
    """Run all background async tasks."""
    async def safe_send(text):
        try:
            await send_message(text)
        except Exception as e:
            print(f"❌ Alert send error: {e}")

    tasks = [
        briefing_loop(safe_send),
        reminder_loop(safe_send),
    ]

    # Only monitor server if configured
    if ORACLE_HOST != "your_oracle_server_ip":
        tasks.append(monitor_loop(safe_send))
        print("✅ Server monitoring: ON")
    else:
        print("⚠️  Server monitoring: OFF (set ORACLE_HOST in config.py)")

    await asyncio.gather(*tasks)


def start_background():
    """Run background tasks in a separate thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_background_tasks())


if __name__ == "__main__":
    print_banner()
    print("🚀 Starting Jarvis...")
    print("📱 Telegram: Online")
    from config import LLM_PROVIDER
    print(f"🧠 Brain: {LLM_PROVIDER.upper()} (Sinhala High-Accuracy)")
    
    # Start Always-on Voice Listener (for Local PC)
    try:
        from modules.voice_listener import start_listener
        start_listener()
        print("🎙️ Wake Word Listener: ON")
    except Exception as e:
        print(f"⚠️ Voice listener failed to start: {e}")

    print("Open Telegram and message your bot to start!")
    print("Press Ctrl+C to stop.\n")

    # Start Web GUI (Dashboard)
    try:
        from modules.web_gui import run_gui
        threading.Thread(target=run_gui, daemon=True).start()
        print("🌐 Web Dashboard: http://localhost:5000")
    except Exception as e:
        print(f"⚠️ Web GUI failed: {e}")

    # Start Telegram bot (blocking, resilient)
    import time
    import asyncio
    while True:
        try:
            asyncio.set_event_loop(asyncio.new_event_loop())
            run_bot()
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"⚠️ Telegram network error: {e}. Retrying in 5 seconds...")
            time.sleep(5)
