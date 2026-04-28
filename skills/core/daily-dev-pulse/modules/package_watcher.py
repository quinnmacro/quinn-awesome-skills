"""Package watcher for Daily Dev Pulse.

Checks npm and PyPI for available updates to configured dependencies.
Uses presearch skill for package trend discovery as an optional enrichment.
"""

import json
import os
import subprocess
import urllib.request
import urllib.error
from datetime import datetime, timezone

from config import get_dependencies, get_tech_stack, load_config

NPM_API = "https://registry.npmjs.org"
PYPI_API = "https://pypi.org/pypi"


def _find_presearch_script():
    """Locate presearch's presearch.sh script."""
    candidates = [
        os.path.expanduser("~/.claude/skills/presearch/scripts/presearch.sh"),
        os.path.expanduser("~/.agent/skills/presearch/scripts/presearch.sh"),
    ]
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidates.append(os.path.join(skill_dir, "..", "presearch", "scripts", "presearch.sh"))

    for path in candidates:
        if os.path.isfile(path):
            return path
    return None


def search_package_trends_via_presearch(query):
    """Search for trending packages using presearch skill.

    Returns a dict with trend info, or None on failure.
    """
    presearch_script = _find_presearch_script()
    if not presearch_script:
        return None

    try:
        result = subprocess.run(
            ["bash", presearch_script, query, "json"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode != 0 or not result.stdout.strip():
            return None

        # presearch returns structured search results
        try:
            data = json.loads(result.stdout.strip())
            return {
                "query": query,
                "trends": data if isinstance(data, list) else [data],
                "extraction_method": "presearch",
            }
        except json.JSONDecodeError:
            # If output isn't JSON, treat as raw text
            content = result.stdout.strip()[:300]
            return {
                "query": query,
                "trends": [{"summary": content}],
                "extraction_method": "presearch",
            }
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None


def fetch_npm_info(package):
    """Fetch latest version info from npm registry."""
    try:
        req = urllib.request.Request(
            f"{NPM_API}/{package}/latest",
            headers={"User-Agent": "daily-dev-pulse/1.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())

        return {
            "package": package,
            "registry": "npm",
            "latest_version": data.get("version") or "unknown",
            "description": (data.get("description") or "")[:100],
            "homepage": data.get("homepage") or "",
            "license": data.get("license") or "",
        }
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, Exception):
        return {
            "package": package,
            "registry": "npm",
            "latest_version": "unknown",
            "error": "fetch_failed",
        }


def fetch_pypi_info(package):
    """Fetch latest version info from PyPI."""
    try:
        req = urllib.request.Request(
            f"{PYPI_API}/{package}/json",
            headers={"User-Agent": "daily-dev-pulse/1.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())

        info = data.get("info", {})
        latest_version = data.get("info", {}).get("version") or "unknown"

        # Get URLs for changelog if available
        project_urls = info.get("project_urls", {}) or {}
        changelog_url = (
            project_urls.get("Changelog", "")
            or project_urls.get("History", "")
            or project_urls.get("Changes", "")
            or project_urls.get("Release notes", "")
        )

        return {
            "package": package,
            "registry": "pypi",
            "latest_version": latest_version,
            "description": (info.get("summary") or "")[:100],
            "homepage": info.get("home_page") or "",
            "changelog_url": changelog_url or "",
            "license": info.get("license") or "",
        }
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, Exception):
        return {
            "package": package,
            "registry": "pypi",
            "latest_version": "unknown",
            "error": "fetch_failed",
        }


def watch_packages(config=None):
    """Check all configured dependencies for latest available versions.

    Optionally uses presearch skill for trend discovery on tech stack categories.
    """
    cfg = config or load_config()
    deps = get_dependencies(cfg)
    tech_stack = get_tech_stack(cfg)

    updates = []
    trends = []
    presearch_used = False

    for package in deps.get("npm", []):
        updates.append(fetch_npm_info(package))

    for package in deps.get("pypi", []):
        updates.append(fetch_pypi_info(package))

    # Trend discovery: search for alternatives/trends for tech stack categories
    for framework in (tech_stack.get("frameworks") or [])[:2]:
        trend = search_package_trends_via_presearch(f"{framework} alternative framework trending")
        if trend:
            trends.append(trend)
            presearch_used = True

    # Sort: npm first, then pypi, alphabetically within each group
    updates.sort(key=lambda x: (x.get("registry") or "", x.get("package") or ""))

    return {
        "source": "packages",
        "updates": updates,
        "trends": trends,
        "presearch_used": presearch_used,
        "scan_date": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    data = watch_packages()
    print(json.dumps(data, indent=2))