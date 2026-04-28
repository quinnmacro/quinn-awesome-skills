"""News aggregator for Daily Dev Pulse.

Fetches top stories from HN, Dev.to, Lobsters, and other dev news sources.
"""

import json
import sys
import urllib.request
import urllib.error
from datetime import datetime

from config import get_preferences, load_config

HN_API = "https://hacker-news.firebaseio.com/v0"
DEVTO_API = "https://dev.to/api/articles"
LOBSTERS_API = "https://lobste.rs/latest.json"


def fetch_hn_top(limit=10):
    """Fetch top stories from Hacker News."""
    try:
        req = urllib.request.Request(
            f"{HN_API}/topstories.json",
            headers={"User-Agent": "daily-dev-pulse/1.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            story_ids = json.loads(resp.read().decode())[:limit]

        stories = []
        for sid in story_ids:
            try:
                item_req = urllib.request.Request(
                    f"{HN_API}/item/{sid}.json",
                    headers={"User-Agent": "daily-dev-pulse/1.0"}
                )
                with urllib.request.urlopen(item_req, timeout=5) as item_resp:
                    item = json.loads(item_resp.read().decode())
                if item and item.get("type") == "story":
                    stories.append({
                        "id": sid,
                        "title": item.get("title", ""),
                        "url": item.get("url", f"https://news.ycombinator.com/item?id={sid}"),
                        "score": item.get("score", 0),
                        "comments": item.get("descendants", 0),
                        "source": "hn",
                    })
            except (urllib.error.URLError, json.JSONDecodeError):
                continue

        return stories
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, Exception):
        return []


def fetch_devto_top(limit=10):
    """Fetch trending articles from Dev.to."""
    try:
        req = urllib.request.Request(
            f"{DEVTO_API}?per_page={limit}&top=7",
            headers={"User-Agent": "daily-dev-pulse/1.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            articles = json.loads(resp.read().decode())

        return [
            {
                "id": a.get("id"),
                "title": a.get("title", ""),
                "url": a.get("url", ""),
                "score": a.get("positive_reactions_count", 0),
                "comments": a.get("comments_count", 0),
                "source": "devto",
                "tags": a.get("tag_list", []),
            }
            for a in articles[:limit]
        ]
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, Exception):
        return []


def fetch_lobsters_top(limit=10):
    """Fetch top stories from Lobsters."""
    try:
        req = urllib.request.Request(
            f"{LOBSTERS_API}",
            headers={"User-Agent": "daily-dev-pulse/1.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            stories = json.loads(resp.read().decode())

        return [
            {
                "id": s.get("short_id"),
                "title": s.get("title", ""),
                "url": s.get("url", ""),
                "score": s.get("score", 0),
                "comments": s.get("comment_count", 0),
                "source": "lobsters",
                "tags": s.get("tags", []),
            }
            for s in stories[:limit]
        ]
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, Exception):
        return []


def aggregate_news(config=None):
    """Aggregate news from all configured sources."""
    cfg = config or load_config()
    prefs = get_preferences(cfg)
    sources = prefs.get("news_sources", ["hn", "devto", "lobsters"])

    all_headlines = []

    if "hn" in sources:
        all_headlines.extend(fetch_hn_top(10))

    if "devto" in sources:
        all_headlines.extend(fetch_devto_top(10))

    if "lobsters" in sources:
        all_headlines.extend(fetch_lobsters_top(10))

    # Sort by score descending across all sources
    all_headlines.sort(key=lambda x: x.get("score", 0), reverse=True)

    return {
        "source": "news",
        "headlines": all_headlines[:30],
        "scan_date": datetime.now().isoformat(),
        "sources_checked": sources,
    }


if __name__ == "__main__":
    data = aggregate_news()
    print(json.dumps(data, indent=2))