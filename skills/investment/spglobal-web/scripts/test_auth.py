#!/usr/bin/env python3
"""Quick test of Capital IQ access"""

import json
import sys
from pathlib import Path

AUTH_FILE = Path.home() / ".spglobal" / "auth.json"

def main():
    from playwright.sync_api import sync_playwright

    with open(AUTH_FILE, "r") as f:
        auth = json.load(f)

    print(f"Loaded auth with {len(auth.get('cookies', []))} cookies")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state=auth)
        page = context.new_page()

        # Try main page
        print("\nTrying main page...")
        page.goto("https://www.capitaliq.spglobal.com/", timeout=60000)
        print(f"URL: {page.url}")
        print(f"Title: {page.title()}")

        input("\nPress Enter to close...")
        browser.close()

if __name__ == "__main__":
    main()
