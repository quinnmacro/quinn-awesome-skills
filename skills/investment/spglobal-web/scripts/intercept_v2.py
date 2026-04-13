#!/usr/bin/env python3
"""
Capital IQ Network Interceptor v2
- Opens browser for manual login if needed
- Captures API calls with full headers
- Saves company data directly
"""
import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

PROFILE_DIR = Path.home() / ".spglobal"
COOKIES_FILE = PROFILE_DIR / "cookies.json"
API_CALLS_FILE = PROFILE_DIR / "api_calls.json"
COMPANY_ID = "4004205"  # Apple

async def main():
    print("\n=== Capital IQ Network Interceptor v2 ===\n")

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
    company_data = {}

    async with async_playwright() as p:
        # Use persistent context for session
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR / "browser_profile"),
            headless=False,
            viewport={"width": 1400, "height": 900},
        )

        # Add existing cookies
        if cookies:
            await browser.add_cookies(cookies)

        page = browser.pages[0] if browser.pages else await browser.new_page()

        # Capture API responses
        async def capture_response(response):
            url = response.url
            if "/apisv3/" in url:
                try:
                    headers = dict(response.request.headers)
                    # Capture headers we need
                    relevant_headers = {}
                    for k, v in headers.items():
                        if k.lower() in ['accept', 'content-type', 'x-requested-with',
                         'authorization', 'x-csrf-token', 'x-s-csrf-token',
                         'origin', 'referer', 'sp-request-id']:
                            relevant_headers[k] = v

                    call_info = {
                        "url": url,
                        "method": response.request.method,
                        "status": response.status,
                        "request_headers": relevant_headers,
                    }

                    # Try to get response body
                    try:
                        if "json" in response.headers.get("content-type", ""):
                            body = await response.json()
                            call_info["response"] = body

                            # Look for company data
                            if "company" in url.lower() or "profile" in url.lower():
                                company_data[url] = body
                                print(f"\n[COMPANY DATA] {url[:80]}...")
                    except:
                        pass

                    api_calls.append(call_info)
                    print(f"[API] {response.request.method} {response.status} {url[:80]}...")
                except Exception as e:
                    print(f"Error capturing: {e}")

        page.on("response", capture_response)

        print("\n1. Opening Capital IQ...")
        await page.goto("https://www.capitaliq.spglobal.com/web/client?auth=inherit",
                       wait_until="domcontentloaded", timeout=60000)

        # Check if we need to login
        current_url = page.url
        if "login" in current_url.lower() or "sso" in current_url.lower():
            print("\n[LOGIN REQUIRED] Please login in the browser window...")
            print("Waiting for login (up to 5 minutes)...")

            start = asyncio.get_event_loop().time()
            while asyncio.get_event_loop().time() - start < 300:
                await asyncio.sleep(2)
                current_url = page.url
                if "login" not in current_url.lower() and "sso" not in current_url.lower():
                    print("\n[LOGGED IN]")
                    break

        print(f"\n2. Current URL: {page.url[:80]}...")

        # Navigate to company page
        print(f"\n3. Navigating to Apple company page (ID: {COMPANY_ID})...")
        try:
            await page.goto(
                f"https://www.capitaliq.spglobal.com/web/client?auth=inherit#/company/{COMPANY_ID}",
                wait_until="domcontentloaded",
                timeout=60000
            )
        except Exception as e:
            print(f"Navigation warning: {e}")

        # Wait for data to load
        print("\n4. Waiting for data to load...")
        await asyncio.sleep(5)

        # Scroll to trigger more data loading
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(2)

        # Save captured data
        print(f"\n5. Saving {len(api_calls)} API calls...")
        with open(API_CALLS_FILE, "w", encoding="utf-8") as f:
            json.dump(api_calls, f, indent=2, ensure_ascii=False)
        print(f"   Saved to: {API_CALLS_FILE}")

        # Save company data
        if company_data:
            company_file = PROFILE_DIR / "company_data.json"
            with open(company_file, "w", encoding="utf-8") as f:
                json.dump(company_data, f, indent=2, ensure_ascii=False)
            print(f"   Company data saved to: {company_file}")

        # Save fresh cookies
        fresh_cookies = await browser.cookies()
        with open(COOKIES_FILE, "w") as f:
            json.dump(fresh_cookies, f, indent=2)
        print(f"   Saved {len(fresh_cookies)} cookies")

        # Print header summary
        if api_calls:
            print("\n=== Sample Request Headers ===")
            sample = api_calls[0]
            print(f"URL: {sample['url'][:100]}")
            print(f"Method: {sample['method']}")
            print("Headers:")
            for k, v in sample.get('request_headers', {}).items():
                print(f"  {k}: {v[:80]}...")

        input("\nPress Enter to close browser...")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
