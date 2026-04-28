#!/usr/bin/env bash
# Daily Dev Pulse - Orchestration script
# Collects data from all sources and pipes to formatter
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MODULES_DIR="${SCRIPT_DIR}/../modules"

# Parse arguments
FORMAT="terminal"
REPOS="all"
FOCUS="all"
DAYS="7"
CONFIG_PATH="${PULSE_CONFIG_PATH:-$HOME/.quinn-skills/pulse-config.yml}"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --format)
            FORMAT="$2"
            shift 2
            ;;
        --repos)
            REPOS="$2"
            shift 2
            ;;
        --focus)
            FOCUS="$2"
            shift 2
            ;;
        --days)
            DAYS="$2"
            shift 2
            ;;
        --config)
            CONFIG_PATH="$2"
            shift 2
            ;;
        *)
            echo "Usage: daily-dev-pulse.sh [--format terminal|md|json] [--repos all|owner/repo,...] [--focus security|news|activity|all] [--days 1|7|30] [--config path]"
            exit 1
            ;;
    esac
done

# Export config path for Python modules
export PULSE_CONFIG_PATH="${CONFIG_PATH}"

# Check gh CLI availability
GH_AVAILABLE=false
if command -v gh &>/dev/null && gh auth status &>/dev/null 2>&1; then
    GH_AVAILABLE=true
fi

# Create temp directory for data collection
TMPDIR="$(mktemp -d)"
trap 'rm -rf "${TMPDIR}"' EXIT

# Collect data based on focus
COMBINED_DATA="{"

# GitHub activity
if [[ "${FOCUS}" == "all" || "${FOCUS}" == "activity" ]]; then
    if [[ "${GH_AVAILABLE}" == "true" ]]; then
        echo "📡 Scanning GitHub repos..." >&2
        python3 "${MODULES_DIR}/github_scanner.py" > "${TMPDIR}/github.json" 2>/dev/null || echo '{"source":"github","repos":[],"error":"scan_failed"}' > "${TMPDIR}/github.json"
    else
        echo "⚠️ gh CLI not available or not authenticated — skipping GitHub scan" >&2
        echo '{"source":"github","repos":[],"error":"gh_not_available"}' > "${TMPDIR}/github.json"
    fi
    GITHUB_DATA="$(cat "${TMPDIR}/github.json")"
    COMBINED_DATA="${COMBINED_DATA}\"github\":${GITHUB_DATA},"
fi

# Security alerts
if [[ "${FOCUS}" == "all" || "${FOCUS}" == "security" ]]; then
    echo "🛡️ Checking security alerts..." >&2
    python3 "${MODULES_DIR}/security_checker.py" > "${TMPDIR}/security.json" 2>/dev/null || echo '{"source":"security","alerts":[],"error":"check_failed"}' > "${TMPDIR}/security.json"
    SECURITY_DATA="$(cat "${TMPDIR}/security.json")"
    COMBINED_DATA="${COMBINED_DATA}\"security\":${SECURITY_DATA},"
fi

# Package updates
if [[ "${FOCUS}" == "all" || "${FOCUS}" == "activity" ]]; then
    echo "📦 Checking package updates..." >&2
    python3 "${MODULES_DIR}/package_watcher.py" > "${TMPDIR}/packages.json" 2>/dev/null || echo '{"source":"packages","updates":[],"error":"check_failed"}' > "${TMPDIR}/packages.json"
    PACKAGES_DATA="$(cat "${TMPDIR}/packages.json")"
    COMBINED_DATA="${COMBINED_DATA}\"packages\":${PACKAGES_DATA},"
fi

# News aggregation
if [[ "${FOCUS}" == "all" || "${FOCUS}" == "news" ]]; then
    echo "📰 Aggregating dev news..." >&2
    python3 "${MODULES_DIR}/news_aggregator.py" > "${TMPDIR}/news.json" 2>/dev/null || echo '{"source":"news","headlines":[],"error":"fetch_failed"}' > "${TMPDIR}/news.json"
    NEWS_DATA="$(cat "${TMPDIR}/news.json")"
    COMBINED_DATA="${COMBINED_DATA}\"news\":${NEWS_DATA},"
fi

# Remove trailing comma and close JSON
COMBINED_DATA="${COMBINED_DATA%,}}"
COMBINED_DATA="${COMBINED_DATA},\"scan_date\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}"

# Write combined data to temp file
echo "${COMBINED_DATA}" > "${TMPDIR}/combined.json"

# Format output
echo "🎨 Formatting output (${FORMAT})..." >&2
python3 "${SCRIPT_DIR}/pulse_formatter.py" --format "${FORMAT}" < "${TMPDIR}/combined.json"

echo "" >&2
echo "✅ Daily Dev Pulse complete" >&2