#!/usr/bin/env python3
"""
Capital IQ Direct API Fetcher
Uses captured JWT token from browser to make API calls directly.
"""
import json
import sys
from pathlib import Path
from curl_cffi import requests

PROFILE_DIR = Path.home() / ".spglobal"
API_CALLS_FILE = PROFILE_DIR / "api_calls.json"
COMPANY_ID = "4004205"  # Apple

def get_auth_token():
    """Extract authorization token from captured API calls"""
    if not API_CALLS_FILE.exists():
        return None

    with open(API_CALLS_FILE, "r", encoding="utf-8") as f:
        calls = json.load(f)

    for call in calls:
        headers = call.get("request_headers", {})
        auth = headers.get("authorization", "")
        if auth.startswith("Bearer "):
            return auth

    return None

def get_csrf_token():
    """Get CSRF token from saved cookies"""
    cookies_file = PROFILE_DIR / "cookies.json"
    if not cookies_file.exists():
        return None

    with open(cookies_file, "r", encoding="utf-8") as f:
        cookies = json.load(f)

    for c in cookies:
        if "csrf" in c.get("name", "").lower():
            return c.get("value")

    return None

def fetch_company(company_id: str):
    """Fetch company data using captured token"""
    token = get_auth_token()
    if not token:
        print("[ERROR] No auth token found. Run intercept_v2.py first.")
        return None

    csrf_token = get_csrf_token()
    print(f"Using token: {token[:50]}...")
    print(f"CSRF token: {csrf_token[:30] if csrf_token else 'Not found'}...")

    session = requests.Session(impersonate="chrome120")

    # Set headers from captured request
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.9",
        "Authorization": token,
        "Origin": "https://www.capitaliq.spglobal.com",
        "Referer": "https://www.capitaliq.spglobal.com/web/client?auth=inherit",
        "X-Requested-With": "XMLHttpRequest",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    if csrf_token:
        headers["X-SP-CSRF-Token"] = csrf_token

    # Try different API endpoints for company data
    endpoints = [
        f"/apisv3/spg-webplatform-core/company/profile?id={company_id}",
        f"/apisv3/company-service/v1/companies/{company_id}",
        f"/apisv3/spg-webplatform-core/company/{company_id}",
        f"/apisv3/company-service/v1/Company({company_id})",
    ]

    base_url = "https://www.capitaliq.spglobal.com"

    for endpoint in endpoints:
        url = base_url + endpoint
        print(f"\nTrying: {endpoint}")

        try:
            response = session.get(url, headers=headers, timeout=30)
            print(f"Status: {response.status_code}")
            print(f"Content-Type: {response.headers.get('content-type', '')}")

            if "json" in response.headers.get('content-type', ''):
                data = response.json()
                print(f"JSON keys: {list(data.keys())[:10] if isinstance(data, dict) else 'list'}")
                return data
            else:
                print(f"Got HTML/other content: {response.text[:200]}")

        except Exception as e:
            print(f"Error: {e}")

    return None

def main():
    company_id = sys.argv[1] if len(sys.argv) > 1 else COMPANY_ID
    print(f"\n=== Fetching company: {company_id} ===\n")

    data = fetch_company(company_id)

    if data:
        print("\n=== Company Data ===")
        print(json.dumps(data, indent=2, ensure_ascii=False)[:2000])
    else:
        print("\n[ERROR] Could not fetch company data")

if __name__ == "__main__":
    main()
