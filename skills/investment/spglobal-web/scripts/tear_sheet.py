#!/usr/bin/env python3
"""
Capital IQ Tear Sheet Generator
Usage: python tear_sheet.py <ticker> [--output <directory>]
"""

import json
import os
import sys
import re
import time
import argparse
from pathlib import Path
from datetime import datetime
from urllib.parse import quote

# Capital IQ URL patterns
CIQ_BASE = "https://www.capitaliq.spglobal.com"
CIQ_COMPANY = f"{CIQ_BASE}/company"

# Persistent browser profile
PROFILE_DIR = Path.home() / ".spglobal" / "browser_profile"


def check_profile():
    """Check if browser profile exists"""
    if not PROFILE_DIR.exists():
        print(f"\n[ERROR] No browser profile found at {PROFILE_DIR}")
        print("Run: python login.py\n")
        return False
    return True


def extract_text_safe(element) -> str:
    """Safely extract text from an element"""
    try:
        return element.inner_text().strip() if element else ""
    except:
        return ""


def generate_tear_sheet(page, ticker: str) -> dict:
    """Generate a tear sheet for a company"""

    # Search for company first
    search_url = f"{CIQ_BASE}/web/controller/snippet/snp_search_snippet?typeahead_search_input={quote(ticker)}"
    page.goto(search_url, wait_until="networkidle", timeout=60000)
    time.sleep(3)

    # Find company link
    company_link = page.query_selector("a[href*='/company/']")
    if not company_link:
        return {"error": f"Company not found: {ticker}"}

    href = company_link.get_attribute("href") or ""
    match = re.search(r'/company/([^/]+)', href)
    if not match:
        return {"error": f"Could not extract company ID from {href}"}

    company_id = match.group(1)
    company_name = extract_text_safe(company_link)

    print(f"Found: {company_name} ({company_id})")

    # Data structure
    tear_sheet = {
        "ticker": ticker,
        "company_name": company_name,
        "company_id": company_id,
        "generated_at": datetime.now().isoformat(),
        "overview": {},
        "financials": {},
        "valuation": {},
        "key_stats": {},
        "peers": [],
        "description": ""
    }

    # 1. Company Overview Page
    print("Fetching company overview...")
    page.goto(f"{CIQ_COMPANY}/{company_id}", wait_until="networkidle", timeout=60000)
    time.sleep(3)

    # Extract overview data
    try:
        # Company description
        desc_el = page.query_selector("[class*='description'], [class*='business'], .company-description")
        if desc_el:
            tear_sheet["description"] = extract_text_safe(desc_el)[:1000]

        # Key stats from overview
        stat_labels = page.query_selector_all("[class*='stat-label'], [class*='label']")
        stat_values = page.query_selector_all("[class*='stat-value'], [class*='value']")

        for i, label in enumerate(stat_labels):
            if i < len(stat_values):
                key = extract_text_safe(label).lower().replace(" ", "_").replace(":", "")
                value = extract_text_safe(stat_values[i])
                if key and value:
                    tear_sheet["key_stats"][key] = value

    except Exception as e:
        print(f"  [WARN] Error extracting overview: {e}")

    # 2. Financials Page
    print("Fetching financials...")
    try:
        page.goto(f"{CIQ_COMPANY}/{company_id}/financials", wait_until="networkidle", timeout=60000)
        time.sleep(3)

        # Extract key financial metrics
        financials_data = {}
        rows = page.query_selector_all("tr")
        for row in rows:
            cells = row.query_selector_all("td, th")
            if len(cells) >= 2:
                label = extract_text_safe(cells[0]).lower()
                values = [extract_text_safe(c) for c in cells[1:4]]  # Get first 3 periods
                if label and values[0]:
                    financials_data[label] = values

        tear_sheet["financials"] = financials_data

    except Exception as e:
        print(f"  [WARN] Error extracting financials: {e}")

    # 3. Valuation Page
    print("Fetching valuation...")
    try:
        page.goto(f"{CIQ_COMPANY}/{company_id}/valuation", wait_until="networkidle", timeout=60000)
        time.sleep(3)

        valuation_data = {}
        # Look for valuation metrics
        metrics = ["P/E", "EV/EBITDA", "P/B", "P/S", "EV/Revenue"]
        page_text = page.content()

        for metric in metrics:
            pattern = rf"{metric}[:\s]*([\d.]+)"
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                valuation_data[metric] = match.group(1)

        tear_sheet["valuation"] = valuation_data

    except Exception as e:
        print(f"  [WARN] Error extracting valuation: {e}")

    # 4. Peers/Competitors
    print("Fetching peers...")
    try:
        page.goto(f"{CIQ_COMPANY}/{company_id}/peers", wait_until="networkidle", timeout=60000)
        time.sleep(3)

        peers = []
        peer_links = page.query_selector_all("a[href*='/company/']")
        for link in peer_links[:10]:  # Limit to 10 peers
            peer_name = extract_text_safe(link)
            if peer_name and peer_name != company_name:
                peers.append(peer_name)

        tear_sheet["peers"] = peers

    except Exception as e:
        print(f"  [WARN] Error extracting peers: {e}")

    return tear_sheet


def format_markdown(tear_sheet: dict) -> str:
    """Format tear sheet as Markdown"""

    md = f"""# {tear_sheet.get('company_name', 'Company')} ({tear_sheet.get('ticker', 'N/A')})

> Generated: {tear_sheet.get('generated_at', 'N/A')}
> Source: Capital IQ

## Overview

| Metric | Value |
|--------|-------|
"""

    for key, value in tear_sheet.get("key_stats", {}).items():
        md += f"| {key.replace('_', ' ').title()} | {value} |\n"

    if tear_sheet.get("description"):
        md += f"\n### Business Description\n\n{tear_sheet['description']}\n"

    if tear_sheet.get("valuation"):
        md += "\n## Valuation Metrics\n\n| Metric | Value |\n|--------|-------|\n"
        for metric, value in tear_sheet["valuation"].items():
            md += f"| {metric} | {value} |\n"

    if tear_sheet.get("financials"):
        md += "\n## Key Financials\n\n"
        for metric, values in tear_sheet["financials"].items():
            if len(values) >= 1 and values[0]:
                md += f"- **{metric.title()}**: {' | '.join(values[:3])}\n"

    if tear_sheet.get("peers"):
        md += f"\n## Peer Companies\n\n"
        for peer in tear_sheet["peers"]:
            md += f"- {peer}\n"

    md += "\n---\n*Data sourced from S&P Capital IQ*\n"

    return md


def main():
    parser = argparse.ArgumentParser(description="Generate Capital IQ Tear Sheet")
    parser.add_argument("ticker", help="Stock ticker or company name")
    parser.add_argument("--output", "-o", default=None, help="Output directory")
    parser.add_argument("--format", "-f", choices=["markdown", "json"], default="markdown")

    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("  Capital IQ Tear Sheet Generator")
    print("=" * 60)

    # Check profile
    if not check_profile():
        return 1

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("\n[ERROR] Playwright not installed")
        print("Install with: uv pip install playwright && playwright install chromium\n")
        return 1

    print(f"\nUsing browser profile: {PROFILE_DIR}")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=True
        )
        page = context.pages[0] if context.pages else context.new_page()

        try:
            tear_sheet = generate_tear_sheet(page, args.ticker)

            if "error" in tear_sheet:
                print(f"\n[ERROR] {tear_sheet['error']}\n")
                return 1

            # Format output
            if args.format == "json":
                output = json.dumps(tear_sheet, indent=2, ensure_ascii=False)
            else:
                output = format_markdown(tear_sheet)

            # Determine output path
            if args.output:
                output_dir = Path(args.output)
            else:
                output_dir = Path.home() / ".spglobal" / "exports"

            output_dir.mkdir(parents=True, exist_ok=True)
            ext = ".json" if args.format == "json" else ".md"
            output_file = output_dir / f"{args.ticker}_tear_sheet{ext}"

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(output)

            print("\n" + "-" * 60)
            print("  Tear Sheet Content")
            print("-" * 60)
            print(output[:2000])
            if len(output) > 2000:
                print("\n... (truncated)")

            print(f"\n[SUCCESS] Saved to: {output_file}")

        except Exception as e:
            print(f"\n[ERROR] {e}")
            return 1

        finally:
            context.close()

    print("\n" + "=" * 60 + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
