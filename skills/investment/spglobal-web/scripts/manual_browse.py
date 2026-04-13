#!/usr/bin/env python3
"""
Capital IQ Manual Browser - For testing and URL discovery
Usage: python manual_browse.py
"""

import sys
import time
from pathlib import Path
from datetime import datetime

PROFILE_DIR = Path.home() / ".spglobal" / "browser_profile"
CIQ_BASE = "https://www.capitaliq.spglobal.com"


def main():
    print("\n" + "=" * 60)
    print("  Capital IQ Manual Browser")
    print("=" * 60)
    print("\n  Instructions:")
    print("  1. Browser will open to Capital IQ homepage")
    print("  2. Navigate and search for companies manually")
    print("  3. Press Ctrl+C in this terminal to save current URL")
    print("  4. Or wait 5 minutes for auto-close")
    print("\n  Find the URL patterns for:")
    print("  - Company search results")
    print("  - Company profile page")
    print("  - Financials page")
    print("=" * 60 + "\n")

    from playwright.sync_api import sync_playwright

    visited_urls = []

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            args=["--start-maximized"]
        )
        page = context.pages[0] if context.pages else context.new_page()

        # Track URL changes
        def on_url_change():
            url = page.url
            if url and url not in visited_urls:
                visited_urls.append(url)
                print(f"  [URL] {url}")

        # Set up URL monitoring
        try:
            page.goto(CIQ_BASE, wait_until="networkidle", timeout=60000)
        except Exception as e:
            print(f"  [WARN] Initial load: {e}")

        print(f"\n  Current URL: {page.url}")
        print("\n  Browse the site. URLs will be logged here.")
        print("  Press Ctrl+C when done to save visited URLs.\n")

        start_time = time.time()
        try:
            while time.time() - start_time < 300:  # 5 min timeout
                current_url = page.url
                if current_url and current_url not in visited_urls:
                    visited_urls.append(current_url)
                    print(f"  [{datetime.now().strftime('%H:%M:%S')}] {current_url}")
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n  [INTERRUPTED] Saving visited URLs...")

        # Save visited URLs
        urls_file = Path.home() / ".spglobal" / "visited_urls.txt"
        with open(urls_file, "w", encoding="utf-8") as f:
            for url in visited_urls:
                f.write(url + "\n")

        print(f"\n  Visited URLs saved to: {urls_file}")
        print("\n  Visited URLs:")
        for url in visited_urls:
            print(f"    {url}")

        context.close()

    print("\n" + "=" * 60 + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
