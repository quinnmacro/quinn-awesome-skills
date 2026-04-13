#!/usr/bin/env python3
"""
Capital IQ Login - Using nodriver
"""
import json
import sys
import asyncio
import time
from pathlib import Path

PROFILE_DIR = Path.home() / ".spglobal"
COOKIES_FILE = PROFILE_DIR / "cookies.json"

print("\n=== Capital IQ Login ===\n", flush=True)
print("Using nodriver for anti-bot bypass\n", flush=True)

async def main():
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    print("Importing nodriver...", flush=True)
    import nodriver

    print("Starting browser...", flush=True)
    browser = await nodriver.start()

    print("Navigating to Capital IQ...", flush=True)
    page = await browser.get("https://www.capitaliq.spglobal.com/")

    print("\n--- Browser opened! ---", flush=True)
    print("1. Login to Capital IQ in the browser", flush=True)
    print("2. Script will auto-detect login (up to 5 min)\n", flush=True)

    start = time.time()
    logged_in = False

    while time.time() - start < 300:
        try:
            url = page.target.url if hasattr(page, 'target') else ""
            elapsed = int(time.time() - start)

            if elapsed % 10 == 0:  # Print every 10 seconds
                print(f"[{elapsed}s] Waiting for login... URL: {url[:50]}...", flush=True)

            if url and "login" not in url.lower() and "sso" not in url.lower():
                content = await page.get_content()
                if len(content) > 1000 and "503" not in content:
                    logged_in = True
                    print(f"\n[{elapsed}s] Login detected!", flush=True)
                    break
        except Exception as e:
            print(f"Error: {e}", flush=True)

        await asyncio.sleep(3)

    # Save cookies
    print("\nSaving cookies...", flush=True)
    try:
        cookies = await browser.cookies.get_all()
        cookie_list = []
        for c in cookies:
            if hasattr(c, '__dict__'):
                cookie_list.append(c.__dict__)
            else:
                cookie_list.append(str(c))

        with open(COOKIES_FILE, "w") as f:
            json.dump(cookie_list, f, indent=2)

        print(f"Saved {len(cookie_list)} cookies to: {COOKIES_FILE}", flush=True)
    except Exception as e:
        print(f"Could not save cookies: {e}", flush=True)

    browser.stop()
    print("\n=== Done! Run: python fetch_curl.py AAPL ===\n", flush=True)
    return 0

if __name__ == "__main__":
    try:
        sys.exit(asyncio.run(main()))
    except KeyboardInterrupt:
        print("\nInterrupted", flush=True)
        sys.exit(0)
