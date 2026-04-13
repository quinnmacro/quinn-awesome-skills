#!/usr/bin/env python3
"""
Capital IQ Network Interceptor v3 - Using nodriver for anti-bot bypass
"""
import asyncio
import json
from pathlib import Path

PROFILE_DIR = Path.home() / ".spglobal"
COOKIES_FILE = PROFILE_DIR / "cookies.json"
API_CALLS_FILE = PROFILE_DIR / "api_calls.json"
COMPANY_ID = "4004205"  # Apple

async def main():
    print("\n=== Capital IQ Network Interceptor v3 (nodriver) ===\n")

    # Load cookies
    cookies_list = []
    if COOKIES_FILE.exists():
        with open(COOKIES_FILE, "r", encoding="utf-8") as f:
            cookies_raw = json.load(f)
            for c in cookies_raw:
                cookies_list.append(c)
        print(f"Loaded {len(cookies_list)} cookies")

    print("Starting browser with nodriver...")
    import nodriver

    browser = await nodriver.start()

    print("\nNavigating to Capital IQ...")
    page = await browser.get("https://www.capitaliq.spglobal.com/web/client?auth=inherit")

    print("Waiting for page to load...")
    await asyncio.sleep(5)

    # Navigate to company page
    company_url = f"https://www.capitaliq.spglobal.com/web/client?auth=inherit#/company/{COMPANY_ID}"
    print(f"\nNavigating to Apple company page: {company_url}")
    page = await browser.get(company_url)

    print("Waiting for company data to load...")
    await asyncio.sleep(10)

    # Get page content
    content = await page.get_content()
    print(f"Page content length: {len(content)}")

    # Save page content
    with open(PROFILE_DIR / "page_content.html", "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Saved page content to: {PROFILE_DIR / 'page_content.html'}")

    # Try to get cookies
    try:
        fresh_cookies = await browser.cookies.get_all()
        cookie_list = []
        for c in fresh_cookies:
            if hasattr(c, '__dict__'):
                cookie_list.append(c.__dict__)
            else:
                cookie_list.append(str(c))

        with open(COOKIES_FILE, "w", encoding="utf-8") as f:
            json.dump(cookie_list, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(cookie_list)} fresh cookies")
    except Exception as e:
        print(f"Could not save cookies: {e}")

    print("\n=== Done ===")
    browser.stop()

if __name__ == "__main__":
    asyncio.run(main())
