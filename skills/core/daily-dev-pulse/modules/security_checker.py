"""Security/CVE checker for Daily Dev Pulse.

Checks public CVE databases for vulnerabilities in configured tech stack.
Uses NVD API (National Vulnerability Database) — no key required (rate-limited).
"""

import json
import sys
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime, timedelta

from config import get_tech_stack, load_config

NVD_API_BASE = "https://services.nvd.nist.gov/rest/json/cves/2.0"
NVD_RATE_LIMIT_SECONDS = 6  # Without API key, 5 requests per 30 seconds


def build_search_terms(tech_stack):
    """Build CVE search terms from tech stack config."""
    terms = []

    python_version = tech_stack.get("python", "")
    if python_version:
        terms.append({"product": "python", "version": python_version})

    for framework in tech_stack.get("frameworks", []):
        terms.append({"product": framework.lower(), "version": ""})

    for db in tech_stack.get("databases", []):
        terms.append({"product": db.lower(), "version": ""})

    for lib in tech_stack.get("libraries", []):
        terms.append({"product": lib.lower(), "version": ""})

    return terms


def fetch_cves(product, version="", days=30):
    """Fetch recent CVEs for a product from NVD API."""
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%dT00:00:00.000")

    params = {
        "keywordSearch": product,
        "pubStartDate": start_date,
        "resultsPerPage": 10,
    }

    if version:
        params["keywordSearch"] = f"{product} {version}"

    query = "&".join(f"{k}={urllib.parse.quote_plus(str(v))}" for k, v in params.items())
    url = f"{NVD_API_BASE}?{query}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "daily-dev-pulse/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, Exception):
        return []

    vulnerabilities = data.get("vulnerabilities", [])
    results = []

    for vuln in vulnerabilities[:10]:
        cve = vuln.get("cve", {})
        cve_id = cve.get("id", "")
        descriptions = cve.get("descriptions", [])
        desc = ""
        for d in descriptions:
            if d.get("lang") == "en":
                desc = d.get("value", "")
                break

        metrics = cve.get("metrics", {})
        severity = "unknown"
        score = 0.0

        cvss_v31 = metrics.get("cvssMetricV31", [])
        if cvss_v31:
            severity = cvss_v31[0].get("cvssData", {}).get("baseSeverity", "unknown")
            score = cvss_v31[0].get("cvssData", {}).get("baseScore", 0.0)
        elif metrics.get("cvssMetricV30"):
            severity = metrics.get("cvssMetricV30")[0].get("cvssData", {}).get("baseSeverity", "unknown")
            score = metrics.get("cvssMetricV30")[0].get("cvssData", {}).get("baseScore", 0.0)

        results.append({
            "cve_id": cve_id,
            "product": product,
            "severity": severity,
            "score": score,
            "description": desc[:200],
            "published": cve.get("published", "")[:10],
        })

    return results


def check_security(config=None, days=30):
    """Check all tech stack components for recent CVEs."""
    cfg = config or load_config()
    tech_stack = get_tech_stack(cfg)
    terms = build_search_terms(tech_stack)

    all_alerts = []
    for term in terms:
        cves = fetch_cves(term["product"], term.get("version", ""), days)
        all_alerts.extend(cves)

    # Sort by severity score descending
    all_alerts.sort(key=lambda x: x.get("score", 0), reverse=True)

    # Deduplicate by CVE ID
    seen = set()
    unique_alerts = []
    for alert in all_alerts:
        if alert["cve_id"] not in seen:
            seen.add(alert["cve_id"])
            unique_alerts.append(alert)

    return {
        "source": "security",
        "alerts": unique_alerts[:20],
        "scan_date": datetime.now().isoformat(),
        "tech_stack_checked": tech_stack,
    }


if __name__ == "__main__":
    data = check_security()
    print(json.dumps(data, indent=2))