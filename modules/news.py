# modules/news.py - News Skill
import requests
from config import NEWS_API_KEY

def get_top_news(limit=3):
    """Fetch top headlines."""
    if not NEWS_API_KEY:
        return "📰 Top News: (No News API key set in Jarvis settings)"
        
    try:
        url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"
        res = requests.get(url, timeout=5)
        data = res.json()
        
        if data["status"] == "ok":
            articles = data["articles"][:limit]
            news_list = [f"• {a['title']}" for a in articles]
            return "📰 *Top Headlines:*\n" + "\n".join(news_list)
        return "❌ News API error."
    except:
        return "❌ Failed to fetch news."
