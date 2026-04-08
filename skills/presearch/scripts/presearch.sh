#!/usr/bin/env bash
# Presearch - 开发前搜索现有方案
# Usage: presearch.sh <query> [format]
# Example: presearch.sh "React framework" emoji
set -euo pipefail

QUERY="${1:?Usage: presearch.sh <query> [format]}"
FORMAT="${2:-table}"

# 设置模块路径
export PRESEARCH_MODULES="$(dirname "$0")/../modules"

python3 "$PRESEARCH_MODULES/presearch_core.py" "$QUERY" -f "$FORMAT"
