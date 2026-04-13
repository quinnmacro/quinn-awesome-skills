#!/usr/bin/env python3
"""
Capital IQ Company Data Fetcher - Using nodriver (anti-bot bypass)
Usage: python fetch_company.py <ticker or company name>
"""

import json
import sys
import asyncio
import time
from pathlib import Path
from urllib.parse import quote

# Paths
PROFILE_DIR = Path.home() / ".spglobal"
COOKIES_FILE = PROFILE_DIR / "cookies.json"

# Capital IQ URLs
CIQ_BASE = "https://www.capitaliq.spglobal.com"
CIQ_SEARCH_API = f"{CIQ_BASE}/apisv3/spg-webplatform-core/search/searchResults"


def check_cookies():
    """Check if cookies file exists"""
    if not COOKIES_FILE.exists():
        print(f"\n  [ERROR] No cookies found at {COOKIES_FILE}")
        print("  Run: python login.py\n")
        return False
    return True


async def search_company(page, query: str) -> dict:
    """Search for a company"""
    print(f"\n  Searching for: {query}")

    # Method 1: Try direct company page
    if len(query) <= 5 and query.isalpha():
        direct_url = f"{CIQ_BASE}/company/{query.upper()}"
        print(f"  Trying direct URL: {direct_url}")
        try:
            await page.goto(direct_url)
            await asyncio.sleep(3)

            # Check if page loaded successfully
            content = await page.get_content()
            if "503" not in content and "error" not in content.lower():
                print(f"  Direct match found!")
                return {
                    "name": query.upper(),
                    "id": query.upper(),
                    "url": direct_url
                }
        except Exception as e:
            print(f"  Direct lookup failed: {e}")

    # Method 2: Use search API
    search_url = f"{CIQ_SEARCH_API}?vertical=&q={quote(query)}"
    print(f"  Trying search API: {search_url}")

    try:
        await page.goto(search_url)
        await asyncio.sleep(3)

        content = await page.get_content()
        print(f"  Response length: {len(content)}")

        # Try to extract JSON from response
        import re
        json_match = re.search(r'<pre[^>]*>([^<]+)</pre>', content)
        if json_match:
            data = json.loads(json_match.group(1))
        else:
            # Try body content
            body_match = re.search(r'<body[^>]*>([^<]+)</body>', content, re.DOTALL)
            if body_match:
                text = body_match.group(1).strip()
                if text.startswith("{") or text.startswith("["):
                    data = json.loads(text)
                else:
                    print(f"  Response: {text[:500]}")
                    return None

        # Parse results
        results = []
        if isinstance(data, dict):
            items = data.get("results", data.get("items", data.get("data", [])))
            if not isinstance(items, list):
                items = [data] if data else []

            for item in items[:5]:
                company_id = (
                    item.get("id") or
                    item.get("companyId") or
                    item.get("iqId") or
                    item.get("targetId")
                )
                name = (
                    item.get("name") or
                    item.get("companyName") or
                    item.get("title") or
                    item.get("targetName")
                )
                if company_id and name:
                    results.append({
                        "name": name,
                        "id": company_id,
                        "url": f"{CIQ_BASE}/company/{company_id}"
                    })

        return results[0] if results else None

    except Exception as e:
        print(f"  [ERROR] Search failed: {e}")
        return None


async def get_company_profile(page, company_id: str) -> dict:
    """Fetch company profile"""
    print(f"  Fetching profile for: {company_id}")

    profile_url = f"{CIQ_BASE}/company/{company_id}"
    await page.goto(profile_url)
    await asyncio.sleep(3)

    data = {
        "id": company_id,
        "url": profile_url,
        "name": None,
        "ticker": None,
        "description": None
    }

    try:
        content = await page.get_content()
        import re

        # Company name from h1
        match = re.search(r'<h1[^>]*>([^<]+)</h1>', content)
        if match:
            data["name"] = match.group(1).strip()

        # Description from meta
        match = re.search(r'<meta[^>]*name="description"[^>]*content="([^"]+)"', content)
        if match:
            data["description"] = match.group(1)

    except Exception as e:
        print(f"  [WARN] Error extracting data: {e}")

    return data


async def main_async():
    if len(sys.argv) < 2:
        print("\n  Usage: python fetch_company.py <ticker or company name>")
        print("  Example: python fetch_company.py AAPL\n")
        return 1

    query = sys.argv[1]

    print("\n" + "=" * 60)
    print("  Capital IQ Company Fetcher (Anti-Bot Bypass)")
    print("=" * 60)

    if not check_cookies():
        return 1

    try:
        import nodriver
    except ImportError:
        print("\n  [ERROR] nodriver not installed")
        print("  Install with: uv pip install nodriver --system\n")
        return 1

    print(f"\n  Starting browser with anti-bot bypass...")

    browser = await nodriver.start()
    page = await browser.get("about:blank")

    try:
        # Load cookies
        with open(COOKIES_FILE, "r") as f:
            cookies = json.load(f)
        print(f"  Loaded {len(cookies)} cookies")

        # Set cookies
        for cookie in cookies:
            try:
                if isinstance(cookie, dict):
                    await browser.cookies.set(cookie.get('name', ''), cookie.get('value', ''))
            except:
                pass

        # Search for company
        company = await search_company(page, query)

        if not company:
            print(f"\n  [ERROR] Company not found: {query}\n")
            return 1

        print(f"  Found: {company['name']} ({company['id']})")

        # Get profile
        profile = await get_company_profile(page, company['id'])

        result = {
            "query": query,
            "company": company,
            "profile": profile
        }

        print("\n" + "-" * 60)
        print("  Company Data")
        print("-" * 60)
        print(json.dumps(result, indent=2, ensure_ascii=False))

        # Save
        output_file = PROFILE_DIR / "cache" / f"{query}.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"\n  Saved to: {output_file}")

    except Exception as e:
        print(f"\n  [ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        await browser.stop()

    print("\n" + "=" * 60 + "\n")
    return 0


def main():
    return asyncio.run(main_async())


if __name__ == "__main__":
    sys.exit(main())
