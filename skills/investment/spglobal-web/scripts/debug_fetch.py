#!/usr/bin/env python3
"""
Capital IQ Company Data Fetcher - Debug Mode
Usage: python fetch_company.py <ticker>
"""

import json
import sys
import time
from pathlib import Path

PROFILE_DIR = Path.home() / ".spglobal" / "browser_profile"
CIQ_BASE = "https://www.capitaliq.spglobal.com"


def main():
    if len(sys.argv) < 2:
        print("\n  Usage: python fetch_company.py <ticker>\n")
        return 1

    query = sys.argv[1]

    print("\n" + "=" * 60)
    print("  Capital IQ Fetcher (Visible Mode)")
    print("=" * 60)

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        # Launch with visible browser
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,  # Visible browser
            args=["--start-maximized"]
        )
        page = context.pages[0] if context.pages else context.new_page()

        try:
            # Go to company page
            url = f"{CIQ_BASE}/company/{query.upper()}"
            print(f"\n  Navigating to: {url}")
            page.goto(url, wait_until="networkidle", timeout=60000)
            time.sleep(3)

            print(f"  Current URL: {page.url}")
            print(f"  Page title: {page.title()}")

            # Take screenshot
            screenshot_file = Path.home() / ".spglobal" / f"{query}_debug.png"
            page.screenshot(path=str(screenshot_file))
            print(f"\n  Screenshot saved: {screenshot_file}")

            # Get page content sample
            content = page.content()
            print(f"  Page content length: {len(content)}")

            # Save HTML for debugging
            html_file = Path.home() / ".spglobal" / f"{query}_debug.html"
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"  HTML saved: {html_file}")

            # Try to extract company name
            name_el = page.query_selector("h1")
            if name_el:
                print(f"\n  Company name (h1): {name_el.inner_text().strip()}")

            # Wait for user to see the page
            print("\n  Press Enter to close browser...")
            input()

        except Exception as e:
            print(f"\n  [ERROR] {e}")
            import traceback
            traceback.print_exc()

        finally:
            context.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
