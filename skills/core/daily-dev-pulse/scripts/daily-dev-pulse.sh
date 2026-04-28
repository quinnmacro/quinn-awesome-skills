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

# Export config path and CLI overrides for Python modules
export PULSE_CONFIG_PATH="${CONFIG_PATH}"
export PULSE_LOOKBACK_DAYS="${DAYS}"
export PULSE_REPOS="${REPOS}"

# Check gh CLI availability
GH_AVAILABLE=false
if command -v gh &>/dev/null && gh auth status &>/dev/null 2>&1; then
    GH_AVAILABLE=true
fi

# Create temp directory for data collection
TMPDIR="$(mktemp -d)"
trap 'rm -rf "${TMPDIR}"' EXIT

# Collect data based on focus, writing each source to its own file
if [[ "${FOCUS}" == "all" || "${FOCUS}" == "activity" ]]; then
    if [[ "${GH_AVAILABLE}" == "true" ]]; then
        echo "Scanning GitHub repos..." >&2
        python3 "${MODULES_DIR}/github_scanner.py" > "${TMPDIR}/github.json" 2>/dev/null || \
            echo '{"source":"github","repos":[],"error":"scan_failed"}' > "${TMPDIR}/github.json"
    else
        echo "gh CLI not available or not authenticated - skipping GitHub scan" >&2
        echo '{"source":"github","repos":[],"error":"gh_not_available"}' > "${TMPDIR}/github.json"
    fi

    echo "Checking package updates..." >&2
    python3 "${MODULES_DIR}/package_watcher.py" > "${TMPDIR}/packages.json" 2>/dev/null || \
        echo '{"source":"packages","updates":[],"error":"check_failed"}' > "${TMPDIR}/packages.json"
fi

if [[ "${FOCUS}" == "all" || "${FOCUS}" == "security" ]]; then
    echo "Checking security alerts..." >&2
    python3 "${MODULES_DIR}/security_checker.py" > "${TMPDIR}/security.json" 2>/dev/null || \
        echo '{"source":"security","alerts":[],"error":"check_failed"}' > "${TMPDIR}/security.json"
fi

if [[ "${FOCUS}" == "all" || "${FOCUS}" == "news" ]]; then
    echo "Aggregating dev news..." >&2
    python3 "${MODULES_DIR}/news_aggregator.py" > "${TMPDIR}/news.json" 2>/dev/null || \
        echo '{"source":"news","headlines":[],"error":"fetch_failed"}' > "${TMPDIR}/news.json"
fi

# Merge all collected JSON files into combined output using Python
# (shell string concatenation is fragile with JSON data)
python3 -c "
import json, os, sys
from datetime import datetime, timezone

tmpdir = os.environ.get('PULSE_TMPDIR', '${TMPDIR}')
combined = {}
combined['scan_date'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

for key in ['github', 'security', 'packages', 'news']:
    fpath = os.path.join(tmpdir, key + '.json')
    if os.path.exists(fpath):
        try:
            with open(fpath) as f:
                combined[key] = json.load(f)
        except (json.JSONDecodeError, IOError):
            combined[key] = {'source': key, 'error': 'data_corrupted'}

json.dump(combined, sys.stdout, ensure_ascii=False)
" PULSE_TMPDIR="${TMPDIR}" > "${TMPDIR}/combined.json"

# Format output
echo "Formatting output (${FORMAT})..." >&2
python3 "${SCRIPT_DIR}/pulse_formatter.py" --format "${FORMAT}" < "${TMPDIR}/combined.json"

echo "" >&2
echo "Daily Dev Pulse complete" >&2