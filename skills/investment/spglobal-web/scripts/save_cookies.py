#!/usr/bin/env python3
"""
Capital IQ Cookie Saver - Manual Method
Usage: python save_cookies.py

Instructions:
1. Open Capital IQ in your browser and login
2. Open Developer Tools (F12) -> Application -> Cookies
3. Copy all cookies as JSON and paste when prompted

Or use this bookmarklet in console:
copy(JSON.stringify(document.cookie.split('; ').map(c => {
  const [name, ...rest] = c.split('=');
  return {name, value: rest.join('=')};
})))
"""

import json
import sys
from pathlib import Path

PROFILE_DIR = Path.home() / ".spglobal"
COOKIES_FILE = PROFILE_DIR / "cookies.json"
AUTH_FILE = PROFILE_DIR / "auth.json"

def main():
    print("\n" + "=" * 60)
    print("  Capital IQ Cookie Saver")
    print("=" * 60)

    print("""
  Method 1: From Browser Console
  ------------------------------
  1. Open https://www.capitaliq.spglobal.com/ in Chrome
  2. Login if needed
  3. Open DevTools (F12) -> Console tab
  4. Paste this code and press Enter:

     copy(JSON.stringify(document.cookie.split('; ').map(c => {
       const [name, ...rest] = c.split('=');
       return {name, value: rest.join('=')};
     })))

  5. The cookies are now copied to clipboard
  6. Paste them below

  Method 2: From Network Tab
  --------------------------
  1. Open DevTools -> Network tab
  2. Refresh the page
  3. Click any request -> Headers -> Request Headers -> Cookie
  4. Copy the full cookie string

""")

    print("  Paste your cookies (JSON format or name=value pairs):")
    print("  (Press Ctrl+D or Ctrl+Z then Enter when done)")
    print("-" * 60 + "\n")

    try:
        lines = []
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass

    input_text = "\n".join(lines).strip()

    if not input_text:
        print("\n  [ERROR] No input provided\n")
        return 1

    # Parse input
    cookies = []

    # Try JSON first
    if input_text.startswith("["):
        try:
            cookies = json.loads(input_text)
        except:
            pass
    # Try name=value pairs
    elif "=" in input_text:
        for pair in input_text.split(";"):
            pair = pair.strip()
            if "=" in pair:
                name, value = pair.split("=", 1)
                cookies.append({"name": name.strip(), "value": value.strip()})

    if not cookies:
        print("\n  [ERROR] Could not parse cookies\n")
        return 1

    # Save
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    # Save as cookies.json
    with open(COOKIES_FILE, "w") as f:
        json.dump(cookies, f, indent=2)
    print(f"\n  Saved {len(cookies)} cookies to: {COOKIES_FILE}")

    # Also save as auth.json format (for compatibility)
    auth = {"cookies": cookies}
    with open(AUTH_FILE, "w") as f:
        json.dump(auth, f, indent=2)
    print(f"  Saved to: {AUTH_FILE}")

    print("\n" + "=" * 60)
    print("  Next: python fetch_curl.py AAPL")
    print("=" * 60 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
