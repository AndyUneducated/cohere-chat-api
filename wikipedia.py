import requests

WIKI_API = "https://en.wikipedia.org/w/api.php"


def search(query):
    """Search Wiki, return a list of {title, snippet}."""
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srlimit": 5,
        "format": "json",
    }
    headers = {
        "User-Agent": "CohereChatHomework/0.1 (school project)"
    }

    r = requests.get(WIKI_API, params=params, headers=headers, timeout=10)
    r.raise_for_status()

    data = r.json()

    results = []
    for item in data.get("query", {}).get("search", []):
        results.append({
            "title": item.get("title", ""),
            "snippet": item.get("snippet", ""),
        })
        
    return results
