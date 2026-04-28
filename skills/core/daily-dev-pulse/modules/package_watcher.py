"""Package watcher for Daily Dev Pulse.

Checks npm and PyPI for available updates to configured dependencies.
"""

import json
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone

from config import get_dependencies, load_config

NPM_API = "https://registry.npmjs.org"
PYPI_API = "https://pypi.org/pypi"


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
            "latest_version": data.get("version", "unknown"),
            "description": (data.get("description", "") or "")[:100],
            "homepage": data.get("homepage", ""),
            "license": data.get("license", ""),
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
        latest_version = data.get("info", {}).get("version", "unknown")

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
            "description": (info.get("summary", "") or "")[:100],
            "homepage": info.get("home_page", ""),
            "changelog_url": changelog_url,
            "license": info.get("license", ""),
        }
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, Exception):
        return {
            "package": package,
            "registry": "pypi",
            "latest_version": "unknown",
            "error": "fetch_failed",
        }


def watch_packages(config=None):
    """Check all configured dependencies for latest available versions."""
    cfg = config or load_config()
    deps = get_dependencies(cfg)

    updates = []

    for package in deps.get("npm", []):
        updates.append(fetch_npm_info(package))

    for package in deps.get("pypi", []):
        updates.append(fetch_pypi_info(package))

    # Sort: npm first, then pypi, alphabetically within each group
    updates.sort(key=lambda x: (x["registry"], x["package"]))

    return {
        "source": "packages",
        "updates": updates,
        "scan_date": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    data = watch_packages()
    print(json.dumps(data, indent=2))