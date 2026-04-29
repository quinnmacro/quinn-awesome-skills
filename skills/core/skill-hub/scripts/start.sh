#!/usr/bin/env bash
# Start the Skill Hub web server
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODULES_DIR="$SCRIPT_DIR/modules"
PORT="${SKILL_HUB_PORT:-8765}"

echo "Starting Skill Hub on http://localhost:$PORT"
python3 "$MODULES_DIR/app.py"