# modules/wikipedia_skill.py - Wikipedia access for Jarvis
import wikipedia

def search_wiki(query, lang="en"):
    """Search wikipedia for a summary."""
    try:
        wikipedia.set_lang(lang)
        # Search for the best match
        search_results = wikipedia.search(query)
        if not search_results:
            return f"🔍 I couldn't find anything on Wikipedia for '{query}', Ravi."
            
        summary = wikipedia.summary(search_results[0], sentences=3)
        return f"📖 *From Wikipedia:* \n\n{summary}"
    except wikipedia.DisambiguationError as e:
        return f"🔍 There are multiple results for '{query}'. Could you be more specific? (e.g., {e.options[:3]})"
    except Exception as e:
        return f"❌ Wiki error: {e}"
