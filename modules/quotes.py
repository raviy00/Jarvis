# modules/quotes.py - Inspirational Quotes for Jarvis
import requests

def get_random_quote():
    """Fetch a random inspirational quote."""
    try:
        # Using Quotable (Free open-source API)
        response = requests.get("https://api.quotable.io/random", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return f"📜 *'{data['content']}'*\n— {data['author']}"
        return "❌ I couldn't find a quote right now, Ravi."
    except:
        # Fallback to a hardcoded one if the API is down
        return "📜 *'The only way to do great work is to love what you do.'*\n— Steve Jobs"

def get_joke():
    """Fetch a random joke."""
    try:
        response = requests.get("https://official-joke-api.appspot.com/random_joke", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return f"😄 *{data['setup']}*\n... {data['punchline']}"
        return "❌ No jokes today. Back to work!"
    except:
        return "😄 Why did the programmer quit his job? Because he didn't get arrays (a raise)!"
