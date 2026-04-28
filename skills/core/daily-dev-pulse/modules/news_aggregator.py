"""News aggregator for Daily Dev Pulse.

Fetches top stories from HN, Dev.to, Lobsters, and other dev news sources.
Uses url-fetcher skill for article content extraction as a fallback.
"""

import json
import os
import subprocess
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

from config import get_preferences, load_config

HN_API = "https://hacker-news.firebaseio.com/v0"
DEVTO_API = "https://dev.to/api/articles"
LOBSTERS_API = "https://lobste.rs/latest.json"


def _find_url_fetcher_script():
    """Locate url-fetcher's fetch.sh script."""
    candidates = [
        os.path.expanduser("~/.claude/skills/url-fetcher/scripts/fetch.sh"),
        os.path.expanduser("~/.agent/skills/url-fetcher/scripts/fetch.sh"),
    ]
    # Also try relative to this skill's directory
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidates.append(os.path.join(skill_dir, "..", "url-fetcher", "scripts", "fetch.sh"))

    for path in candidates:
        if os.path.isfile(path):
            return path
    return None


def fetch_article_via_url_fetcher(url):
    """Fetch article content via url-fetcher's fetch.sh as a fallback.

    Returns a dict with title and content summary, or None on failure.
    """
    fetch_script = _find_url_fetcher_script()
    if not fetch_script:
        return None

    try:
        result = subprocess.run(
            ["bash", fetch_script, url],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode != 0 or not result.stdout.strip():
            return None

        content = result.stdout.strip()
        # Extract title from markdown frontmatter or first line
        lines = content.split("\n")
        title = ""
        for line in lines:
            if line.startswith("title:"):
                title = line.split("title:", 1)[1].strip().strip('"').strip("'")
                break

        if not title:
            # Try first # heading
            for line in lines:
                if line.startswith("# "):
                    title = line.removeprefix("# ").strip()
                    break

        # Summary: first 3 non-empty, non-frontmatter content lines
        summary_lines = []
        in_frontmatter = False
        for line in lines:
            if line.strip() == "---":
                in_frontmatter = not in_frontmatter
                continue
            if in_frontmatter:
                continue
            if line.strip():
                summary_lines.append(line.strip())
            if len(summary_lines) >= 3:
                break

        return {
            "title": title or url,
            "content_summary": " ".join(summary_lines)[:200],
            "source_url": url,
            "extraction_method": "url-fetcher",
        }
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None


def _fetch_hn_item(sid):
    """Fetch a single HN story item by ID. Returns story dict or None."""
    try:
        item_req = urllib.request.Request(
            f"{HN_API}/item/{sid}.json",
            headers={"User-Agent": "daily-dev-pulse/1.0"}
        )
        with urllib.request.urlopen(item_req, timeout=5) as item_resp:
            item = json.loads(item_resp.read().decode())
        if item and item.get("type") == "story":
            return {
                "id": sid,
                "title": item.get("title", ""),
                "url": item.get("url", f"https://news.ycombinator.com/item?id={sid}"),
                "score": item.get("score", 0),
                "comments": item.get("descendants", 0),
                "source": "hn",
            }
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, Exception):
        pass
    return None


def fetch_hn_top(limit=10):
    """Fetch top stories from Hacker News using concurrent requests."""
    try:
        req = urllib.request.Request(
            f"{HN_API}/topstories.json",
            headers={"User-Agent": "daily-dev-pulse/1.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            story_ids = json.loads(resp.read().decode())[:limit]

        stories = []
        with ThreadPoolExecutor(max_workers=min(limit, 5)) as executor:
            futures = {executor.submit(_fetch_hn_item, sid): sid for sid in story_ids}
            for future in as_completed(futures):
                result = future.result()
                if result:
                    stories.append(result)

        # Preserve original order by sorting by story_id position
        id_order = {sid: i for i, sid in enumerate(story_ids)}
        stories.sort(key=lambda s: id_order.get(s.get("id", ""), 0))

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
    """Aggregate news from all configured sources.

    Uses url-fetcher as fallback when direct API fails for a source.
    """
    cfg = config or load_config()
    prefs = get_preferences(cfg)
    sources = prefs.get("news_sources", ["hn", "devto", "lobsters"])

    all_headlines = []
    url_fetcher_used = False

    if "hn" in sources:
        hn_headlines = fetch_hn_top(10)
        if hn_headlines:
            all_headlines.extend(hn_headlines)
        else:
            # Fallback: use url-fetcher to fetch HN front page content
            fallback = fetch_article_via_url_fetcher("https://news.ycombinator.com")
            if fallback:
                all_headlines.append({
                    "id": "hn-fallback",
                    "title": fallback["title"],
                    "url": "https://news.ycombinator.com",
                    "score": 0,
                    "comments": 0,
                    "source": "hn",
                    "content_summary": fallback.get("content_summary", ""),
                })
                url_fetcher_used = True

    if "devto" in sources:
        devto_headlines = fetch_devto_top(10)
        if devto_headlines:
            all_headlines.extend(devto_headlines)
        else:
            fallback = fetch_article_via_url_fetcher("https://dev.to/trending")
            if fallback:
                all_headlines.append({
                    "id": "devto-fallback",
                    "title": fallback["title"],
                    "url": "https://dev.to/trending",
                    "score": 0,
                    "comments": 0,
                    "source": "devto",
                    "content_summary": fallback.get("content_summary", ""),
                })
                url_fetcher_used = True

    if "lobsters" in sources:
        lobsters_headlines = fetch_lobsters_top(10)
        if lobsters_headlines:
            all_headlines.extend(lobsters_headlines)
        else:
            fallback = fetch_article_via_url_fetcher("https://lobste.rs")
            if fallback:
                all_headlines.append({
                    "id": "lobsters-fallback",
                    "title": fallback["title"],
                    "url": "https://lobste.rs",
                    "score": 0,
                    "comments": 0,
                    "source": "lobsters",
                    "content_summary": fallback.get("content_summary", ""),
                })
                url_fetcher_used = True

    # Sort by score descending across all sources
    all_headlines.sort(key=lambda x: x.get("score", 0), reverse=True)

    return {
        "source": "news",
        "headlines": all_headlines[:30],
        "scan_date": datetime.now(timezone.utc).isoformat(),
        "sources_checked": sources,
        "url_fetcher_used": url_fetcher_used,
    }


if __name__ == "__main__":
    data = aggregate_news()
    print(json.dumps(data, indent=2))