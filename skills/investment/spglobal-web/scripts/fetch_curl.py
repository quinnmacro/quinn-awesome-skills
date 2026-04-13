#!/usr/bin/env python3
"""
Capital IQ Fetcher - Using curl_cffi (browser fingerprint impersonation)
Usage: python fetch_curl.py <ticker>
"""

import json
import sys
from pathlib import Path
from urllib.parse import quote

PROFILE_DIR = Path.home() / ".spglobal"
AUTH_FILE = PROFILE_DIR / "auth.json"

CIQ_BASE = "https://www.capitaliq.spglobal.com"
CIQ_SEARCH_API = f"{CIQ_BASE}/apisv3/spg-webplatform-core/search/searchResults"


def load_cookies():
    """Load cookies from auth.json"""
    cookies = {}

    if AUTH_FILE.exists():
        with open(AUTH_FILE, "r") as f:
            auth = json.load(f)
            for cookie in auth.get("cookies", []):
                name = cookie.get("name")
                value = cookie.get("value")
                if name and value:
                    cookies[name] = value
        print(f"  Loaded {len(cookies)} cookies")
        return cookies

    return None


def create_session(cookies: dict):
    """Create a session with browser impersonation"""
    from curl_cffi import requests

    session = requests.Session(impersonate="chrome120")

    # Set cookies
    for name, value in cookies.items():
        session.cookies.set(name, value)

    # Set headers
    session.headers.update({
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": f"{CIQ_BASE}/",
        "Origin": CIQ_BASE,
    })

    return session


def refresh_session(session):
    """Visit main page to refresh session"""
    print("  Refreshing session...")

    try:
        response = session.get(f"{CIQ_BASE}/web/client?auth=inherit", timeout=30)
        print(f"  Session refresh status: {response.status_code}")

        # Print new cookies
        print(f"  Cookies after refresh: {len(session.cookies)}")

        return response.status_code == 200
    except Exception as e:
        print(f"  Session refresh error: {e}")
        return False


def search_company(query: str, session) -> dict:
    """Search for company"""
    print(f"\n  Searching for: {query}")

    search_url = f"{CIQ_SEARCH_API}?vertical=&q={quote(query)}"

    try:
        response = session.get(search_url, timeout=30)
        print(f"  Status: {response.status_code}, Content-Type: {response.headers.get('content-type', '')}")

        if response.status_code == 200:
            content_type = response.headers.get("content-type", "")

            if "json" in content_type:
                data = response.json()
                print(f"  JSON response: {json.dumps(data, indent=2)[:500]}")

                # Parse results
                results = []
                items = data.get("results", data.get("items", data.get("data", [])))
                if not isinstance(items, list):
                    items = [data] if data else []

                for item in items[:5]:
                    company_id = item.get("id") or item.get("companyId") or item.get("iqId")
                    name = item.get("name") or item.get("companyName") or item.get("title")
                    if company_id and name:
                        results.append({"name": name, "id": company_id})

                return results[0] if results else None
            else:
                print(f"  HTML response (not JSON)")
                # Check if we need to login
                if "login" in response.text.lower() or "sso" in response.text.lower():
                    print("  [ERROR] Session expired. Run: python login.py")
                else:
                    print(f"  Preview: {response.text[:300]}")
                return None

        elif response.status_code in [401, 403]:
            print("  [ERROR] Authentication required. Run: python login.py")
            return None
        else:
            print(f"  [ERROR] Status: {response.status_code}")
            return None

    except Exception as e:
        print(f"  [ERROR] {e}")
        return None


def main():
    if len(sys.argv) < 2:
        print("\n  Usage: python fetch_curl.py <ticker>")
        print("  Example: python fetch_curl.py AAPL\n")
        return 1

    query = sys.argv[1]

    print("\n" + "=" * 60)
    print("  Capital IQ Fetcher (Browser Fingerprint)")
    print("=" * 60)

    cookies = load_cookies()
    if not cookies:
        print("\n  [ERROR] No cookies. Run: python login.py\n")
        return 1

    session = create_session(cookies)

    # Refresh session
    refresh_session(session)

    # Search
    company = search_company(query, session)

    if not company:
        print(f"\n  [ERROR] Company not found: {query}\n")
        return 1

    print(f"  Found: {company['name']} ({company['id']})")

    result = {"query": query, "company": company}
    print("\n" + "-" * 60)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("-" * 60 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
