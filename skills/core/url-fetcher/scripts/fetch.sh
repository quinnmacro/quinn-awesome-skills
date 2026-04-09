#!/usr/bin/env bash
# Fetch a URL as Markdown via proxy cascade with auto-fallback.
# Usage: fetch.sh <url> [proxy_url]
# Example: fetch.sh https://example.com http://127.0.0.1:7890
#
# Supports social media fixer services (no login required):
# - Twitter/X → fxtwitter.com API
# - Instagram → fxstagram.com
# - TikTok → tnktok.com
# - Reddit → vxreddit.com
# - Threads → fixthreads.seria.moe
# - Bluesky → fxbsky.app
set -euo pipefail

URL="${1:?Usage: fetch.sh <url> [proxy_url]}"
PROXY="${2:-}"

_curl() {
  if [ -n "$PROXY" ]; then
    https_proxy="$PROXY" http_proxy="$PROXY" curl -sL "$@"
  else
    curl -sL "$@"
  fi
}

_has_content() {
  local content="$1"
  local line_count=$(echo "$content" | wc -l | tr -d ' ')

  # Must have more than 5 lines
  [ "$line_count" -gt 5 ] || return 1

  # Filter out common error pages
  echo "$content" | grep -qv "Don't miss what's happening" || return 1
  echo "$content" | grep -qv "Access Denied" || return 1
  echo "$content" | grep -qv "404 Not Found" || return 1

  return 0
}

# ============================================
# Social Media Handlers (from FixTweetBot)
# ============================================

# Twitter/X - uses fxtwitter.com API
fetch_twitter() {
  local url="$1"
  local PARSED=$(python3 -c "
import sys, re
url = sys.argv[1]
m = re.search(r'(x\.com|twitter\.com)/([^/]+)/status/(\d+)', url)
if m:
    print(f'{m.group(2)}|{m.group(3)}')
" "$url" 2>/dev/null)

  local SCREEN_NAME=$(echo "$PARSED" | cut -d'|' -f1)
  local STATUS_ID=$(echo "$PARSED" | cut -d'|' -f2)

  if [ -n "$STATUS_ID" ]; then
    local OUT=$(_curl "https://api.fxtwitter.com/$SCREEN_NAME/status/$STATUS_ID" 2>/dev/null || true)
    if [ -n "$OUT" ] && echo "$OUT" | grep -q '"code":200'; then
      echo "$OUT" | python3 -c "
import sys, json
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
data = json.load(sys.stdin)
tweet = data.get('tweet', {})
author = tweet.get('author', {})
media = tweet.get('media', {})
text = tweet.get('text', '').encode('utf-8', errors='replace').decode('utf-8')
name = author.get('name', '').encode('utf-8', errors='replace').decode('utf-8')
print('---')
print(f'title: \"Tweet by @{author.get(\"screen_name\", \"unknown\")}\"')
print(f'author: \"{name}\"')
print(f'username: \"@{author.get(\"screen_name\", \"\")}\"')
print(f'date: \"{tweet.get(\"created_at\", \"\")}\"')
print(f'tweet_id: \"{tweet.get(\"id\", \"\")}\"')
print(f'likes: {tweet.get(\"likes\", 0)}')
print(f'retweets: {tweet.get(\"retweets\", 0)}')
print(f'views: {tweet.get(\"views\", 0)}')
print(f'url: \"{tweet.get(\"url\", \"\")}\"')
print('---')
print()
print(f'# Tweet by {name} (@{author.get(\"screen_name\", \"\")})')
print()
print(text)
if media.get('videos') or media.get('photos'):
    print()
    for p in media.get('photos', []):
        print(f'![Photo]({p.get(\"url\", \"\")})')
    for v in media.get('videos', []):
        print(f'[Video]({v.get(\"url\", \"\")})')
"
      return 0
    fi
  fi
  return 1
}

# Instagram - uses fxstagram.com
fetch_instagram() {
  local url="$1"
  # Convert to fxstagram.com
  local fixed_url=$(echo "$url" | sed -E 's|instagram\.com|fxstagram.com|')
  local OUT=$(_curl "$fixed_url" 2>/dev/null || true)
  if _has_content "$OUT"; then
    echo "$OUT"
    return 0
  fi
  return 1
}

# TikTok - uses tnktok.com
fetch_tiktok() {
  local url="$1"
  local fixed_url=$(echo "$url" | sed -E 's|tiktok\.com|a.tnktok.com|')
  local OUT=$(_curl "$fixed_url" 2>/dev/null || true)
  if _has_content "$OUT"; then
    echo "$OUT"
    return 0
  fi
  return 1
}

# Reddit - uses vxreddit.com
fetch_reddit() {
  local url="$1"
  local fixed_url=$(echo "$url" | sed -E 's|reddit\.com|vxreddit.com|')
  local OUT=$(_curl "$fixed_url" 2>/dev/null || true)
  if _has_content "$OUT"; then
    echo "$OUT"
    return 0
  fi
  return 1
}

# Threads - uses fixthreads.seria.moe
fetch_threads() {
  local url="$1"
  local fixed_url=$(echo "$url" | sed -E 's|threads\.net|fixthreads.seria.moe|')
  local OUT=$(_curl "$fixed_url" 2>/dev/null || true)
  if _has_content "$OUT"; then
    echo "$OUT"
    return 0
  fi
  return 1
}

# Bluesky - uses fxbsky.app
fetch_bluesky() {
  local url="$1"
  local fixed_url=$(echo "$url" | sed -E 's|bsky\.app|fxbsky.app|')
  local OUT=$(_curl "$fixed_url" 2>/dev/null || true)
  if _has_content "$OUT"; then
    echo "$OUT"
    return 0
  fi
  return 1
}

# ============================================
# Main URL Routing
# ============================================

# Twitter/X - try fxtwitter API first
if echo "$URL" | grep -qE "(twitter\.com|x\.com)/.*status"; then
  if fetch_twitter "$URL"; then
    exit 0
  fi
  # Fallback: Check if we have cookies
  TWITTER_COOKIES="$HOME/.claude/skills/qiaomu-markdown-proxy/twitter_state/cookies.json"
  if [ -f "$TWITTER_COOKIES" ] && [ -s "$TWITTER_COOKIES" ]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    python3 "$SCRIPT_DIR/fetch_twitter.py" "$URL" "$PROXY" 2>&1
    exit $?
  else
    echo "---
title: \"Twitter/X Fetch Failed\"
source: \"$URL\"
---

# Twitter/X Content Unavailable

Could not fetch tweet via API. Options:

1. **Check if the tweet exists** - The tweet may have been deleted
2. **Use cookies method** - Export cookies from your browser

Original URL: $URL
"
    exit 0
  fi
fi

# Instagram
if echo "$URL" | grep -q "instagram\.com"; then
  if fetch_instagram "$URL"; then
    exit 0
  fi
fi

# TikTok
if echo "$URL" | grep -q "tiktok\.com"; then
  if fetch_tiktok "$URL"; then
    exit 0
  fi
fi

# Reddit
if echo "$URL" | grep -q "reddit\.com"; then
  if fetch_reddit "$URL"; then
    exit 0
  fi
fi

# Threads
if echo "$URL" | grep -q "threads\.net"; then
  if fetch_threads "$URL"; then
    exit 0
  fi
fi

# Bluesky
if echo "$URL" | grep -q "bsky\.app"; then
  if fetch_bluesky "$URL"; then
    exit 0
  fi
fi

# 1. r.jina.ai - wide coverage, preserves image links
OUT=$(_curl "https://r.jina.ai/$URL" 2>/dev/null || true)
if _has_content "$OUT"; then
  echo "$OUT"
  exit 0
fi

# 2. defuddle.md - cleaner output with YAML frontmatter
OUT=$(_curl "https://defuddle.md/$URL" 2>/dev/null || true)
if _has_content "$OUT"; then
  echo "$OUT"
  exit 0
fi

# 3. agent-fetch - last resort local tool
if command -v npx &>/dev/null; then
  OUT=$(npx --yes agent-fetch "$URL" --json 2>/dev/null || true)
  if [ -n "$OUT" ]; then
    echo "$OUT"
    exit 0
  fi
fi

echo "ERROR: All fetch methods failed for: $URL" >&2
exit 1
