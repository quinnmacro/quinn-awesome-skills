#!/usr/bin/env python3
"""Quick test if nodriver works"""

import asyncio
import sys

async def main():
    print("Importing nodriver...")
    import nodriver

    print("Starting browser...")
    browser = await nodriver.start()

    print("Browser started!")
    print("Navigating to example.com...")

    page = await browser.get("https://example.com")

    print(f"Page loaded!")

    content = await page.get_content()
    print(f"Content length: {len(content)}")

    await asyncio.sleep(5)

    await browser.stop()
    print("Done!")
    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
