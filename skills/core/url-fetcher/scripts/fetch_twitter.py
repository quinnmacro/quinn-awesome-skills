#!/usr/bin/env python3
"""Fetch Twitter/X tweet as Markdown using saved cookies."""

import json
import sys
import os
import re
import asyncio

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

STATE_DIR = os.path.expanduser("~/.claude/skills/qiaomu-markdown-proxy/twitter_state")
COOKIES_FILE = os.path.join(STATE_DIR, "cookies.json")


def load_cookies():
    """Load cookies from JSON file."""
    if not os.path.exists(COOKIES_FILE):
        return None
    try:
        with open(COOKIES_FILE, 'r') as f:
            cookies = json.load(f)
        if not cookies:
            return None
        # Convert to Playwright format
        playwright_cookies = []
        for cookie in cookies:
            pw_cookie = {
                'name': cookie.get('name', ''),
                'value': cookie.get('value', ''),
                'domain': cookie.get('domain', ''),
                'path': cookie.get('path', '/'),
                'secure': cookie.get('secure', False),
                'httpOnly': cookie.get('httpOnly', False),
            }
            if cookie.get('expirationDate'):
                pw_cookie['expires'] = cookie['expirationDate']
            playwright_cookies.append(pw_cookie)
        return playwright_cookies
    except Exception as e:
        print(f"Error loading cookies: {e}", file=sys.stderr)
        return None


async def fetch_tweet(url: str, proxy: str = None) -> dict:
    """Fetch and parse a Twitter/X tweet using saved cookies."""
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        return {"error": "playwright not installed. Run: pip install playwright && playwright install chromium"}

    # Load cookies
    cookies = load_cookies()
    if not cookies:
        return {
            "error": "No cookies found. Run: python3 ~/.claude/skills/qiaomu-markdown-proxy/scripts/twitter_login.py"
        }

    # Normalize URL
    if "x.com" in url:
        url = url.replace("x.com", "twitter.com")

    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=True)
        except Exception as e:
            return {"error": f"Failed to launch browser: {e}"}

        context_args = {
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        if proxy:
            context_args["proxy"] = {"server": proxy}

        context = await browser.new_context(**context_args)

        # Add cookies
        await context.add_cookies(cookies)

        page = await context.new_page()

        # Retry logic for unstable connections
        last_error = None
        for attempt in range(3):
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                break
            except Exception as e:
                last_error = e
                if attempt < 2:
                    await asyncio.sleep(2)
                    continue
                await browser.close()
                return {"error": f"Failed to load page after 3 attempts: {last_error}"}

        await asyncio.sleep(3)  # Wait for dynamic content

        try:
            # Check if we're logged in
            if await page.query_selector('[data-testid="LoginForm"]'):
                await browser.close()
                return {"error": "Session expired. Please re-export cookies from your browser."}

            page_text = await page.inner_text("body")

            # Extract tweet ID
            match = re.search(r"/status/(\d+)", url)
            tweet_id = match.group(1) if match else ""

            # Extract tweet text
            tweet_text_el = await page.query_selector('[data-testid="tweetText"]')
            content = ""
            if tweet_text_el:
                content = await tweet_text_el.inner_text()

            # Check for errors only if no content found
            if not content:
                if "Something went wrong" in page_text or "Try again" in page_text:
                    await browser.close()
                    return {"error": "Tweet not found or has been deleted"}
                if "this page doesn't exist" in page_text.lower():
                    await browser.close()
                    return {"error": "Tweet not found or has been deleted"}

            # Extract author info
            author = ""
            author_el = await page.query_selector('[data-testid="User-Name"]')
            if author_el:
                author = await author_el.inner_text()

            # Extract username
            username = ""
            username_els = await page.query_selector_all('a[role="link"]')
            for el in username_els:
                href = await el.get_attribute('href')
                text = await el.inner_text()
                if href and text.startswith('@') and '/status/' not in href:
                    username = text
                    break

            # Extract date
            date = ""
            time_el = await page.query_selector("time")
            if time_el:
                date = await time_el.get_attribute("datetime") or ""

            # Extract images
            images = []
            img_els = await page.query_selector_all('[data-testid="tweetPhoto"] img')
            for img in img_els:
                src = await img.get_attribute("src")
                if src:
                    images.append(src)

            await browser.close()

            if not content and not images:
                return {"error": "Could not extract tweet content"}

            return {
                "tweet_id": tweet_id,
                "author": author.replace("\n", " ").strip(),
                "username": username.strip(),
                "date": date,
                "content": content,
                "images": images,
                "url": url,
            }

        except Exception as e:
            await browser.close()
            return {"error": f"Failed to fetch tweet: {e}"}


def format_as_markdown(result: dict) -> str:
    """Format result dict as a Markdown document."""
    if "error" in result:
        return f"Error: {result['error']}"

    parts = ["---"]
    if result.get("author"):
        parts.append(f'author: "{result["author"]}"')
    if result.get("username"):
        parts.append(f'username: "{result["username"]}"')
    if result.get("date"):
        parts.append(f'date: "{result["date"]}"')
    if result.get("tweet_id"):
        parts.append(f'tweet_id: "{result["tweet_id"]}"')
    parts.append(f'url: "{result["url"]}"')
    parts.append("---")
    parts.append("")

    if result.get("author"):
        parts.append(f'# Tweet by {result["author"]}')
        parts.append("")

    if result.get("content"):
        parts.append(result["content"])

    if result.get("images"):
        parts.append("")
        for i, img_url in enumerate(result["images"], 1):
            parts.append(f"![Image {i}]({img_url})")

    return "\n".join(parts)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: fetch_twitter.py <twitter_url> [proxy]", file=sys.stderr)
        print("First setup cookies: python3 twitter_login.py", file=sys.stderr)
        sys.exit(1)

    url = sys.argv[1]
    proxy = sys.argv[2] if len(sys.argv) > 2 else None
    result = asyncio.run(fetch_tweet(url, proxy))
    print(format_as_markdown(result))
