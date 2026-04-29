#!/usr/bin/env bash
# Daily Dev Pulse - Orchestration script
# Collects data from all sources and pipes to formatter
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MODULES_DIR="${SCRIPT_DIR}/../modules"

# Parse arguments — format defaults to empty so we can fall back to config preference
FORMAT=""
REPOS="all"
FOCUS="all"
DAYS="7"
CONFIG_PATH="${PULSE_CONFIG_PATH:-$HOME/.quinn-skills/pulse-config.yml}"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --format)
            if [[ $# -lt 2 ]]; then
                echo "Error: --format requires a value (terminal|md|json)" >&2
                exit 1
            fi
            FORMAT="$2"
            shift 2
            ;;
        --repos)
            if [[ $# -lt 2 ]]; then
                echo "Error: --repos requires a value" >&2
                exit 1
            fi
            REPOS="$2"
            shift 2
            ;;
        --focus)
            if [[ $# -lt 2 ]]; then
                echo "Error: --focus requires a value (security|news|activity|all)" >&2
                exit 1
            fi
            FOCUS="$2"
            shift 2
            ;;
        --days)
            if [[ $# -lt 2 ]]; then
                echo "Error: --days requires a numeric value" >&2
                exit 1
            fi
            if ! [[ "$2" =~ ^[0-9]+$ ]]; then
                echo "Error: --days requires a positive integer, got '$2'" >&2
                exit 1
            fi
            DAYS="$2"
            shift 2
            ;;
        --config)
            if [[ $# -lt 2 ]]; then
                echo "Error: --config requires a path" >&2
                exit 1
            fi
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
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
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
# Also include preferences (format, stale_pr_days, lookback_days) so the formatter uses config thresholds
PULSE_MODULES_DIR="${MODULES_DIR}" PULSE_TMPDIR="${TMPDIR}" python3 -c "
import json, os, sys
from datetime import datetime, timezone

tmpdir = os.environ.get('PULSE_TMPDIR', '')
if not tmpdir:
    sys.exit(1)
combined = {}
combined['scan_date'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

# Include preferences so formatter can use config-driven thresholds
# Import config.py to get the full preferences dict automatically — no manual key enumeration needed
# This ensures any new preference added to DEFAULT_CONFIG flows through without manual updates
try:
    modules_dir = os.environ.get('PULSE_MODULES_DIR', '')
    if not modules_dir:
        # __file__ is undefined in python3 -c mode, so env var is the only reliable path
        sys.exit(1)
    sys.path.insert(0, modules_dir)
    from config import load_config, get_preferences
    prefs = get_preferences(load_config())
    combined['preferences'] = prefs
except Exception:
    combined['preferences'] = {'stale_pr_days': 3, 'format': 'terminal', 'lookback_days': 7, 'security_lookback_days': 30, 'nvd_rate_limit': 6, 'news_sources': ['hn', 'devto', 'lobsters'], 'max_issues_per_repo': 3, 'max_action_items': 10, 'max_prs_fetch': 20, 'max_ci_runs_fetch': 5, 'max_news_per_source': 10}

for key in ['github', 'security', 'packages', 'news']:
    fpath = os.path.join(tmpdir, key + '.json')
    if os.path.exists(fpath):
        try:
            with open(fpath) as f:
                combined[key] = json.load(f)
        except (json.JSONDecodeError, IOError):
            combined[key] = {'source': key, 'error': 'data_corrupted'}

json.dump(combined, sys.stdout, ensure_ascii=False)
" > "${TMPDIR}/combined.json"

# If --format was not explicitly passed, fall back to config preference
if [[ -z "${FORMAT}" ]]; then
    FORMAT=$(PULSE_TMPDIR="${TMPDIR}" python3 -c "
import json, os, sys
tmpdir = os.environ.get('PULSE_TMPDIR', '')
if not tmpdir:
    print('terminal')
    sys.exit(0)
with open(os.path.join(tmpdir, 'combined.json')) as f:
    data = json.load(f)
print(data.get('preferences', {}).get('format', 'terminal'))
")
fi

# Format output
echo "Formatting output (${FORMAT})..." >&2
python3 "${SCRIPT_DIR}/pulse_formatter.py" --format "${FORMAT}" < "${TMPDIR}/combined.json"

echo "" >&2
echo "Daily Dev Pulse complete" >&2