#!/usr/bin/env python3
"""Test Capital IQ API with session refresh"""

import json
from pathlib import Path
from curl_cffi import requests

PROFILE_DIR = Path.home() / ".spglobal"
COOKIES_FILE = PROFILE_DIR / "cookies.json"

# Load cookies
with open(COOKIES_FILE, "r") as f:
    cookies_list = json.load(f)

cookies = {c["name"]: c["value"] for c in cookies_list}
print(f"Loaded {len(cookies)} cookies")

# Create session
session = requests.Session(impersonate="chrome120")

# Set headers
session.headers.update({
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin": "https://www.capitaliq.spglobal.com",
    "Referer": "https://www.capitaliq.spglobal.com/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
})

for name, value in cookies.items():
    session.cookies.set(name, value)

# Step 1: Visit main page to establish session
print("\n=== Step 1: Visiting main page ===")
response = session.get("https://www.capitaliq.spglobal.com/web/client?auth=inherit", timeout=30)
print(f"Main page status: {response.status_code}")
print(f"Cookies after visit: {len(session.cookies)}")

# Step 2: Test Apple profile API with headers
print("\n=== Step 2: Testing Apple Profile API ===")
url = "https://www.capitaliq.spglobal.com/apisv3/spg-webplatform-core/company/profile?id=4004205"

headers = {
    "Accept": "application/json",
    "X-Requested-With": "XMLHttpRequest",
}

response = session.get(url, headers=headers, timeout=30)
print(f"Status: {response.status_code}")
print(f"Content-Type: {response.headers.get('content-type', '')}")

if "json" in response.headers.get('content-type', ''):
    try:
        data = response.json()
        print(f"\nJSON Response:\n{json.dumps(data, indent=2, ensure_ascii=False)[:3000]}")
    except Exception as e:
        print(f"JSON parse error: {e}")
        print(f"Response: {response.text[:500]}")
else:
    # Check if redirected to login
    if "login" in response.text.lower() or "sso" in response.url:
        print("Session expired - need to re-login")
    else:
        print(f"Got HTML instead of JSON")
        print(f"URL: {response.url}")
        print(f"Preview: {response.text[:500]}")
