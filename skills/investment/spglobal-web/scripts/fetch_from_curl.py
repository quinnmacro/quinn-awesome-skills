#!/usr/bin/env python3
"""
Capital IQ Fetcher - From cURL Command

Usage:
1. Copy a cURL command from browser DevTools (Network tab -> Copy as cURL)
2. Save it to ~/.spglobal/curl_command.txt
3. Run: python fetch_from_curl.py <ticker>

Or paste the cURL command as a string when prompted.
"""
import json
import re
import sys
from pathlib import Path
from curl_cffi import requests

PROFILE_DIR = Path.home() / ".spglobal"
CURL_FILE = PROFILE_DIR / "curl_command.txt"

def parse_curl(curl_command: str) -> dict:
    """Parse cURL command to extract URL, headers, and cookies"""
    result = {
        "url": "",
        "headers": {},
        "cookies": {},
        "method": "GET",
    }

    # Extract URL
    url_match = re.search(r"curl\s+'([^']+)'|curl\s+\"([^\"]+)\"|curl\s+(\S+)", curl_command)
    if url_match:
        result["url"] = url_match.group(1) or url_match.group(2) or url_match.group(3)

    # Extract headers
    header_matches = re.findall(r"-H\s+'([^:]+):\s*([^']+)'|-H\s+\"([^\"]+)\"", curl_command)
    for match in header_matches:
        if match[0] and match[1]:
            key = match[0].strip()
            value = match[1].strip()
            if key.lower() == "cookie":
                # Parse cookies
                for cookie in value.split(";"):
                    if "=" in cookie:
                        name, val = cookie.split("=", 1)
                        result["cookies"][name.strip()] = val.strip()
            else:
                result["headers"][key] = value

    return result

def fetch_company(company_id: str, curl_config: dict):
    """Fetch company data using parsed cURL config"""
    session = requests.Session(impersonate="chrome120")

    # Set cookies
    for name, value in curl_config["cookies"].items():
        session.cookies.set(name, value)

    # Build URL for company
    base_url = "https://www.capitaliq.spglobal.com"
    endpoints = [
        f"/apisv3/spg-webplatform-core/company/profile?id={company_id}",
        f"/apisv3/company-service/v1/companies/{company_id}",
    ]

    headers = curl_config["headers"]

    for endpoint in endpoints:
        url = base_url + endpoint
        print(f"\nTrying: {endpoint}")

        try:
            response = session.get(url, headers=headers, timeout=30)
            print(f"Status: {response.status_code}")
            print(f"Content-Type: {response.headers.get('content-type', '')}")

            if "json" in response.headers.get('content-type', ''):
                return response.json()
            else:
                print(f"Preview: {response.text[:200]}")
        except Exception as e:
            print(f"Error: {e}")

    return None

def main():
    if len(sys.argv) < 2:
        print("\nUsage: python fetch_from_curl.py <company_id>")
        print("Example: python fetch_from_curl.py 4004205\n")
        return 1

    company_id = sys.argv[1]

    # Check for curl command file
    curl_command = ""
    if CURL_FILE.exists():
        with open(CURL_FILE, "r", encoding="utf-8") as f:
            curl_command = f.read().strip()
        print(f"Loaded cURL command from: {CURL_FILE}")
    else:
        print("\nNo cURL command found.")
        print(f"Please save a cURL command to: {CURL_FILE}")
        print("\nOr paste your cURL command:")
        try:
            curl_command = input().strip()
        except EOFError:
            print("\nNo input provided.")
            return 1

    if not curl_command:
        print("No cURL command provided.")
        return 1

    # Parse cURL command
    config = parse_curl(curl_command)
    print(f"\nParsed URL: {config['url'][:80]}...")
    print(f"Headers: {len(config['headers'])}")
    print(f"Cookies: {len(config['cookies'])}")

    # Fetch company
    data = fetch_company(company_id, config)

    if data:
        print("\n=== Company Data ===")
        print(json.dumps(data, indent=2, ensure_ascii=False)[:2000])
    else:
        print("\nCould not fetch company data")

if __name__ == "__main__":
    sys.exit(main() or 0)
