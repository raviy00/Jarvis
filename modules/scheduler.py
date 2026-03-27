# modules/scheduler.py - Morning Briefings and Reminders

import asyncio
import json
import os
from datetime import datetime, timedelta
from modules.brain import think
from config import BRIEFING_HOUR, BRIEFING_MINUTE


REMINDERS_FILE = "data/reminders.json"


def load_reminders():
    if not os.path.exists(REMINDERS_FILE):
        return []
    try:
        with open(REMINDERS_FILE, "r") as f:
            return json.load(f)
    except:
        return []


def save_reminders(reminders):
    os.makedirs("data", exist_ok=True)
    with open(REMINDERS_FILE, "w") as f:
        json.dump(reminders, f, indent=2)


def add_reminder(text, remind_at):
    """Add a reminder. remind_at is datetime string."""
    reminders = load_reminders()
    reminders.append({"text": text, "time": remind_at, "done": False})
    save_reminders(reminders)


def get_morning_briefing():
    """Generate a high-quality morning briefing for Ravi."""
    from modules.weather import get_weather
    from modules.news import get_top_news
    
    weather = get_weather()
    news = get_top_news(limit=2)
    now = datetime.now()
    reminders = load_reminders()
    pending = [r for r in reminders if not r["done"]]
    
    briefing_prompt = f"""You are J.A.R.V.I.S. giving Ravi a morning update.
    Today: {now.strftime('%A, %B %d, %Y')}
    Weather: {weather}
    News: {news}
    Reminders: {len(pending)}
    
    Include:
    - Warm greetings to Ravi
    - Short weather summary
    - High-level news mention
    - Reminder alert if any
    
    Tone: Professional, smart, loyal. No markdown tags in your response. Keep it short (3-4 sentences)."""

    return think(briefing_prompt, [], mode="normal")


async def briefing_loop(send_message_func):
    """Send morning briefing at configured time every day."""
    while True:
        now = datetime.now()
        target = now.replace(hour=BRIEFING_HOUR, minute=BRIEFING_MINUTE, second=0, microsecond=0)

        if now >= target:
            target += timedelta(days=1)

        wait_seconds = (target - now).total_seconds()
        await asyncio.sleep(wait_seconds)

        briefing = get_morning_briefing()
        await send_message_func(f"🌅 *Good Morning Ravi!*\n\n{briefing}")


async def reminder_loop(send_message_func):
    """Check and send due reminders every minute."""
    while True:
        reminders = load_reminders()
        now = datetime.now()
        changed = False

        for r in reminders:
            if not r["done"]:
                try:
                    remind_time = datetime.fromisoformat(r["time"])
                    if now >= remind_time:
                        await send_message_func(f"⏰ *Reminder:* {r['text']}")
                        r["done"] = True
                        changed = True
                except:
                    pass

        if changed:
            save_reminders(reminders)

        await asyncio.sleep(60)
