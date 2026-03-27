# modules/nasa.py - NASA Integration for Jarvis
import requests

NASA_API_URL = "https://api.nasa.gov/planetary/apod"
# Default demo key (works for a limited number of requests per day)
NASA_DEMO_KEY = "DEMO_KEY"

def get_nasa_image():
    """Fetch NASA's Astronomy Picture of the Day (APOD)."""
    try:
        response = requests.get(f"{NASA_API_URL}?api_key={NASA_DEMO_KEY}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            title = data.get("title", "Unknown Title")
            url = data.get("url", "")
            explanation = data.get("explanation", "")
            return f"🌌 *Astronomy Picture of the Day:* \n\n🚩 *{title}*\n📄 {explanation[:300]}...\n\n🔗 [View Full Image]({url})"
        return "❌ NASA mission failed. Maybe try again later."
    except Exception as e:
        return f"❌ Space error: {e}"
