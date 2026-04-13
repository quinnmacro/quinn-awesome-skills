#!/usr/bin/env python3
"""
Capital IQ Network Interceptor - Find actual API calls
Captures network traffic when loading a company page to identify correct API format.
"""
import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

PROFILE_DIR = Path.home() / ".spglobal"
COOKIES_FILE = PROFILE_DIR / "cookies.json"
COMPANY_ID = "4004205"  # Apple

async def main():
    print("\n=== Capital IQ Network Interceptor ===\n")

    # Load cookies
    cookies = []
    if COOKIES_FILE.exists():
        with open(COOKIES_FILE, "r") as f:
            cookies_raw = json.load(f)
            for c in cookies_raw:
                cookies.append({
                    "name": c.get("name"),
                    "value": c.get("value"),
                    "domain": c.get("domain", ".capitaliq.spglobal.com"),
                    "path": c.get("path", "/"),
                })
        print(f"Loaded {len(cookies)} cookies")

    api_calls = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()

        # Add cookies
        await context.add_cookies(cookies)

        # Intercept all requests
        async def capture_request(request):
            url = request.url
            if "/apisv3/" in url or "/api/" in url:
                api_calls.append({
                    "url": url,
                    "method": request.method,
                    "headers": dict(request.headers),
                })
                print(f"[API] {request.method} {url[:100]}...")

        page = await context.new_page()
        page.on("request", capture_request)

        print("\nNavigating to Apple company page...")
        await page.goto(f"https://www.capitaliq.spglobal.com/web/client?auth=inherit#/company/{COMPANY_ID}", wait_until="networkidle")

        print(f"\nCaptured {len(api_calls)} API calls")

        # Wait a bit for more requests
        await asyncio.sleep(3)

        # Save results
        output_file = PROFILE_DIR / "api_calls.json"
        with open(output_file, "w") as f:
            json.dump(api_calls, f, indent=2, ensure_ascii=False)

        print(f"\nSaved to: {output_file}")

        # Print sample
        if api_calls:
            print("\n=== Sample API Call Headers ===")
            sample = api_calls[0]
            print(f"URL: {sample['url']}")
            print(f"Method: {sample['method']}")
            print("Headers:")
            for k, v in sample['headers'].items():
                if k.lower() in ['accept', 'content-type', 'x-requested-with', 'authorization', 'x-csrf-token', 'origin', 'referer']:
                    print(f"  {k}: {v[:100]}")

        input("\nPress Enter to close browser...")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
