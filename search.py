"""
skills/search.py  –  Web search (SerpAPI or DuckDuckGo fallback)
"""
import requests
import logging
from config.settings import SERPAPI_KEY

logger = logging.getLogger(__name__)


def web_search(user_input: str) -> str:
    """Search the web and return a short summary."""
    query = _extract_query(user_input)
    if not query:
        return "What would you like me to search for?"

    if SERPAPI_KEY:
        return _serpapi_search(query)
    return _duckduckgo_search(query)


def _extract_query(text: str) -> str:
    """Strip trigger words to get the bare query."""
    import re
    text = re.sub(r"^(search|google|look up|find|who is|what is)\s+", "", text, flags=re.IGNORECASE)
    return text.strip()


def _serpapi_search(query: str) -> str:
    try:
        r = requests.get(
            "https://serpapi.com/search",
            params={"q": query, "api_key": SERPAPI_KEY, "num": 3},
            timeout=8,
        )
        r.raise_for_status()
        data = r.json()
        results = data.get("organic_results", [])
        if not results:
            return f"No results found for '{query}'."
        top = results[0]
        return f"{top.get('title', '')}: {top.get('snippet', '')} — {top.get('link', '')}"
    except Exception as e:
        logger.error(f"SerpAPI error: {e}")
        return _duckduckgo_search(query)


def _duckduckgo_search(query: str) -> str:
    """DuckDuckGo Instant Answer API (no key required)."""
    try:
        r = requests.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json", "no_html": 1},
            timeout=6,
        )
        r.raise_for_status()
        data = r.json()
        answer = data.get("AbstractText") or data.get("Answer") or ""
        if answer:
            return answer[:400]
        return f"I found some results for '{query}', but no instant answer. Try asking me to search with SerpAPI for richer results."
    except Exception as e:
        logger.error(f"DuckDuckGo error: {e}")
        return "Web search is unavailable at the moment."
