#!/usr/bin/env python3
"""
Login to Twitter by importing cookies from your Chrome browser.

Steps:
1. Open Chrome and login to Twitter (x.com)
2. Install "EditThisCookie" extension: https://chrome.google.com/webstore/detail/editthiscookie/
3. Go to x.com, click the extension, and export cookies as JSON
4. Save the JSON to: ~/.claude/skills/qiaomu-markdown-proxy/twitter_state/cookies.json
"""

import json
import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

STATE_DIR = os.path.expanduser("~/.claude/skills/qiaomu-markdown-proxy/twitter_state")
COOKIES_FILE = os.path.join(STATE_DIR, "cookies.json")


def setup_instructions():
    print("""
==================================================
Twitter Cookie Setup
==================================================

Twitter blocks automated browsers. Use this method instead:

Step 1: Login to Twitter in Chrome
-----------------------------------
Open Chrome and login to https://x.com

Step 2: Install Cookie Export Extension
---------------------------------------
Install "EditThisCookie" or "Cookie Editor" from Chrome Web Store:
https://chrome.google.com/webstore/detail/editthiscookie/

Step 3: Export Cookies
----------------------
1. Go to x.com
2. Click the cookie extension icon
3. Click "Export" button
4. Cookies will be copied to clipboard as JSON

Step 4: Save Cookies
--------------------
Create the file and paste the JSON:

""")

    print(f"File path: {COOKIES_FILE}")
    print()

    # Create directory
    os.makedirs(STATE_DIR, exist_ok=True)

    # Create empty cookies file if not exists
    if not os.path.exists(COOKIES_FILE):
        with open(COOKIES_FILE, 'w') as f:
            f.write('[]')
        print(f"Created empty file: {COOKIES_FILE}")
        print("Please paste your exported cookies JSON into this file.")
    else:
        # Verify existing cookies
        try:
            with open(COOKIES_FILE, 'r') as f:
                cookies = json.load(f)
            if cookies:
                print(f"✅ Found {len(cookies)} cookies in {COOKIES_FILE}")
                # Check for Twitter cookies
                twitter_cookies = [c for c in cookies if 'twitter' in c.get('domain', '') or 'x.com' in c.get('domain', '')]
                if twitter_cookies:
                    print(f"✅ Found {len(twitter_cookies)} Twitter/X cookies")
                    print("\nYou can now fetch tweets!")
                    return True
                else:
                    print("⚠️ No Twitter/X cookies found. Please export cookies from x.com")
            else:
                print("File is empty. Please paste your exported cookies.")
        except json.JSONDecodeError:
            print("⚠️ Invalid JSON in file. Please fix it.")

    return False


def convert_to_playwright_format(cookies):
    """Convert EditThisCookie format to Playwright format."""
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


if __name__ == "__main__":
    setup_instructions()
