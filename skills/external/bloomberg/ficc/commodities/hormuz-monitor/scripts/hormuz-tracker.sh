#!/usr/bin/env bash
# Hormuz Transit Tracker
# Fetch tanker flow data from maritime APIs and normalize it for downstream analysis.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HORMUZ_POLYGON="26.75,56.50;26.75,57.00;25.50,56.50;25.50,57.00"
API_KEY="${MARINETRAFFIC_API_KEY:-}"
DATA_DIR="${HOME}/.cache/hormuz-monitor"
CACHE_FILE="${DATA_DIR}/latest.json"
RAW_CACHE_FILE="${DATA_DIR}/latest.raw.json"
NORMALIZER="${SCRIPT_DIR}/hormuz-normalize.py"
DEFAULT_TRANSIT_PERIOD="24h"
MARINETRAFFIC_URL_STYLE="${MARINETRAFFIC_URL_STYLE:-query}"
MARINETRAFFIC_PROTOCOL="${MARINETRAFFIC_PROTOCOL:-json}"
MARINETRAFFIC_MSGTYPE="${MARINETRAFFIC_MSGTYPE:-extended}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

usage() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  --positions                Fetch current vessel positions in Hormuz"
    echo "  --transit [--period P]     Get transit statistics (24h|7d|30d)"
    echo "  --types                    Vessel type breakdown"
    echo "  --queue                    Queue/waiting vessel count"
    echo "  --all                      Full report (all metrics)"
    echo "  --cache                    Show normalized cached data"
    echo "  --raw-cache                Show raw cached API payload"
    echo "  --help                     Show this help"
    exit 1
}

setup_cache() {
    mkdir -p "${DATA_DIR}"
}

normalize_live_payload() {
    local mode="$1"
    local raw_file="$2"

    python3 "${NORMALIZER}" \
        --mode "${mode}" \
        --input "${raw_file}" \
        --output "${CACHE_FILE}"
}

build_marinetraffic_url() {
    local endpoint="$1"
    local params="$2"
    local path_params

    case "${MARINETRAFFIC_URL_STYLE}" in
        query)
            printf 'https://services.marinetraffic.com/api/%s?%s&key=%s\n' \
                "${endpoint}" "${params}" "${API_KEY}"
            ;;
        path)
            path_params="${params//&//}"
            path_params="${path_params//=/:}"
            if [[ "${path_params}" != *"protocol:"* ]]; then
                path_params="${path_params}/protocol:${MARINETRAFFIC_PROTOCOL}"
            fi
            if [[ -n "${MARINETRAFFIC_MSGTYPE}" && "${path_params}" != *"msgtype:"* ]]; then
                path_params="${path_params}/msgtype:${MARINETRAFFIC_MSGTYPE}"
            fi

            printf 'https://services.marinetraffic.com/api/%s/%s/%s\n' \
                "${endpoint}" "${API_KEY}" "${path_params}"
            ;;
        *)
            echo "${RED}Unsupported MARINETRAFFIC_URL_STYLE: ${MARINETRAFFIC_URL_STYLE}${NC}" >&2
            return 1
            ;;
    esac
}

fetch_marinetraffic() {
    local mode="$1"
    local endpoint="$2"
    local params="$3"
    local tmp_file url

    if [[ -z "${API_KEY}" ]]; then
        echo "${YELLOW}Warning: MARINETRAFFIC_API_KEY not set${NC}"
        echo "Using cached/fallback data..."
        return 1
    fi

    tmp_file="$(mktemp "${DATA_DIR}/marinetraffic.XXXXXX.json")"
    url="$(build_marinetraffic_url "${endpoint}" "${params}")"

    curl -s -f "${url}" -o "${tmp_file}" || {
        echo "${RED}API request failed${NC}"
        rm -f "${tmp_file}"
        return 1
    }

    mv "${tmp_file}" "${RAW_CACHE_FILE}"
    normalize_live_payload "${mode}" "${RAW_CACHE_FILE}" || {
        echo "${RED}API response normalization failed${NC}"
        return 1
    }

    echo "${GREEN}Data fetched and normalized successfully${NC}"
}

fetch_tankertrackers() {
    local tmp_file

    echo "${YELLOW}Fetching from TankerTrackers...${NC}"
    tmp_file="$(mktemp "${DATA_DIR}/tankertrackers.XXXXXX.json")"

    curl -s "https://tankertrackers.com/api/hormuz/latest" -o "${tmp_file}" 2>/dev/null || {
        echo "${RED}TankerTrackers fetch failed${NC}"
        rm -f "${tmp_file}"
        return 1
    }

    mv "${tmp_file}" "${RAW_CACHE_FILE}"
    normalize_live_payload "all" "${RAW_CACHE_FILE}" || {
        echo "${RED}Fallback response normalization failed${NC}"
        return 1
    }
}

generate_sample() {
    cat > "${CACHE_FILE}" <<'SAMPLE'
{
  "timestamp": "2026-05-04T06:00:00Z",
  "source": {
    "provider": "sample",
    "mode": "sample",
    "normalized_from_live_api": false
  },
  "transits_24h": 17,
  "transits_7d_avg": 18.5,
  "vessels": {
    "vlcc": 9,
    "suezmax": 4,
    "aframax": 2,
    "product": 2
  },
  "flow_estimate_mbd": 18.2,
  "queue": {
    "count": 4,
    "avg_wait_hours": 3.5
  },
  "flags": {
    "panama": 35,
    "marshall": 25,
    "liberia": 20,
    "iran": 8,
    "china": 7,
    "others": 5
  },
  "avg_speed_kn": 12.3,
  "risk_signals": {
    "naval_activity": "normal",
    "political_rhetoric": "elevated",
    "insurance_premiums": "stable"
  }
}
SAMPLE
    echo "${GREEN}Sample data generated${NC}"
}

parse_transit_period() {
    local period="${DEFAULT_TRANSIT_PERIOD}"

    case "${2:-}" in
        "")
            ;;
        --period)
            if [[ -z "${3:-}" ]]; then
                echo "${RED}Missing value for --period${NC}"
                usage
            fi
            period="${3}"
            ;;
        --period=*)
            period="${2#--period=}"
            ;;
        24h|7d|30d)
            period="${2}"
            ;;
        *)
            echo "${RED}Unknown transit argument: ${2}${NC}"
            usage
            ;;
    esac

    case "${period}" in
        24h|7d|30d)
            ;;
        *)
            echo "${RED}Unsupported period: ${period}${NC}"
            echo "Supported values: 24h, 7d, 30d"
            exit 1
            ;;
    esac

    printf '%s\n' "${period}"
}

parse_positions() {
    if [[ ! -f "${CACHE_FILE}" ]]; then
        echo "${RED}No cached data available${NC}"
        return 1
    fi

    echo ""
    echo "HORMUZ TRANSIT SUMMARY"
    echo "----------------------------------------"
    echo ""

    jq -r '
        "Timestamp: \(.timestamp)",
        "",
        "Transits (24h): \(.transits_24h) vessels",
        "vs. 7d Avg: \(.transits_7d_avg) vessels",
        "Flow Estimate: \(.flow_estimate_mbd)M bbl/day",
        "",
        "Vessel Types:",
        "  VLCC: \(.vessels.vlcc)",
        "  Suezmax: \(.vessels.suezmax)",
        "  Aframax: \(.vessels.aframax)",
        "  Product: \(.vessels.product)",
        "",
        "Queue:",
        "  Waiting: \(.queue.count) vessels",
        "  Avg Wait: \(.queue.avg_wait_hours)h",
        "",
        "Avg Speed: \(.avg_speed_kn) knots"
    ' "${CACHE_FILE}"
}

parse_types() {
    if [[ ! -f "${CACHE_FILE}" ]]; then
        echo "${RED}No cached data available${NC}"
        return 1
    fi

    echo ""
    echo "VESSEL TYPE BREAKDOWN"
    echo "----------------------------------------"
    echo ""

    jq -r '
        "VLCC (300K bbl): \(.vessels.vlcc) vessels -> \((.vessels.vlcc * 300000 / 1000000) | floor)M bbl capacity",
        "Suezmax (150K): \(.vessels.suezmax) vessels -> \((.vessels.suezmax * 150000 / 1000000) | floor)M bbl",
        "Aframax (80K): \(.vessels.aframax) vessels -> \((.vessels.aframax * 80000 / 1000000) | floor)M bbl",
        "Product (50K): \(.vessels.product) vessels -> \((.vessels.product * 50000 / 1000000) | floor)M bbl",
        "",
        "Total Estimated: \(.flow_estimate_mbd)M bbl/day"
    ' "${CACHE_FILE}"
}

parse_queue() {
    if [[ ! -f "${CACHE_FILE}" ]]; then
        echo "${RED}No cached data available${NC}"
        return 1
    fi

    echo ""
    echo "QUEUE STATUS"
    echo "----------------------------------------"
    echo ""

    jq -r '
        "Vessels Waiting: \(.queue.count)",
        "Normal Range: 3-8",
        "Avg Wait Time: \(.queue.avg_wait_hours) hours",
        "Normal Range: 2-6 hours",
        "",
        "Status: \(if .queue.count > 8 then \"ELEVATED\" elif .queue.count < 3 then \"LOW\" else \"NORMAL\" end)"
    ' "${CACHE_FILE}"
}

parse_risk() {
    if [[ ! -f "${CACHE_FILE}" ]]; then
        echo "${RED}No cached data available${NC}"
        return 1
    fi

    echo ""
    echo "RISK SIGNALS"
    echo "----------------------------------------"
    echo ""

    jq -r '
        "Naval Activity: \(.risk_signals.naval_activity)",
        "Political Rhetoric: \(.risk_signals.political_rhetoric)",
        "Insurance Premiums: \(.risk_signals.insurance_premiums)"
    ' "${CACHE_FILE}"
}

show_all() {
    parse_positions
    echo ""
    parse_types
    echo ""
    parse_queue
    echo ""
    parse_risk
}

setup_cache

case "${1:-}" in
    --positions)
        fetch_marinetraffic "positions" "vessels" "area=${HORMUZ_POLYGON}" || generate_sample
        parse_positions
        ;;
    --transit)
        TRANSIT_PERIOD="$(parse_transit_period "$@")"
        fetch_marinetraffic "transit" "transits" "area=${HORMUZ_POLYGON}&period=${TRANSIT_PERIOD}" || generate_sample
        parse_positions
        ;;
    --types)
        fetch_marinetraffic "types" "vessels" "area=${HORMUZ_POLYGON}&types=tanker" || generate_sample
        parse_types
        ;;
    --queue)
        fetch_marinetraffic "queue" "queue" "port=hormuz" || generate_sample
        parse_queue
        ;;
    --all)
        fetch_marinetraffic "all" "vessels" "area=${HORMUZ_POLYGON}&full=true" || generate_sample
        show_all
        ;;
    --cache)
        if [[ -f "${CACHE_FILE}" ]]; then
            echo "Normalized cache: ${CACHE_FILE}"
            cat "${CACHE_FILE}"
        else
            echo "${RED}No cached data${NC}"
        fi
        ;;
    --raw-cache)
        if [[ -f "${RAW_CACHE_FILE}" ]]; then
            echo "Raw API cache: ${RAW_CACHE_FILE}"
            cat "${RAW_CACHE_FILE}"
        else
            echo "${RED}No raw cached data${NC}"
        fi
        ;;
    --help|-h)
        usage
        ;;
    *)
        generate_sample
        show_all
        ;;
esac
