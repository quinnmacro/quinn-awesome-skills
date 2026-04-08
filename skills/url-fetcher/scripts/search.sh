#!/usr/bin/env bash
# Web Search using open-webSearch (no API key required)
# Usage: search.sh <query> [engine] [limit]
# Example: search.sh "golang tutorial" duckduckgo 5
#
# Engines: bing, duckduckgo, brave, exa, baidu, csdn, juejin, startpage
# Default: duckduckgo
#
# Requires: npx open-websearch@latest
set -euo pipefail

QUERY="${1:?Usage: search.sh <query> [engine] [limit]}"
ENGINE="${2:-duckduckgo}"
LIMIT="${3:-5}"

# Use open-websearch via npx
npx open-websearch@latest search "$QUERY" --engine "$ENGINE" --limit "$LIMIT" --json 2>/dev/null
