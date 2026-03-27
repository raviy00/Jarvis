# modules/search.py - Web Search Skill
from duckduckgo_search import DDGS

def web_search(query):
    """Search the web and return summarized results."""
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=5)]
            if not results:
                return "No search results found."
            
            summary = "\n\n".join([f"✨ {r['title']}\n🔗 {r['href']}\n📜 {r['body']}" for r in results])
            return summary
    except Exception as e:
        print(f"❌ Web search error: {e}")
        return f"Sorry, I had trouble searching the web."
