#!/usr/bin/env bash
# Start, stop, or check status of the Skill Hub web server
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODULES_DIR="$SCRIPT_DIR/../modules"
PORT="${SKILL_HUB_PORT:-8765}"
PID_FILE="${SKILL_HUB_PID_FILE:-$HOME/.quinn-skills/skill-hub.pid}"

LOG_DIR="${SKILL_HUB_LOG_DIR:-$HOME/.quinn-skills}"
LOG_FILE="$LOG_DIR/skill-hub.log"
mkdir -p "$LOG_DIR"

case "${1:-start}" in
  --stop|stop)
    if [ -f "$PID_FILE" ]; then
      PID=$(cat "$PID_FILE")
      if kill -0 "$PID" 2>/dev/null; then
        kill "$PID"
        rm -f "$PID_FILE"
        echo "Skill Hub (PID $PID) stopped."
      else
        rm -f "$PID_FILE"
        echo "Skill Hub process (PID $PID) not running — cleaned stale PID file."
      fi
    else
      echo "No PID file found at $PID_FILE."
      # Try to find by port as fallback
      PID=$(lsof -ti :$PORT 2>/dev/null || true)
      if [ -n "$PID" ]; then
        kill "$PID"
        echo "Skill Hub (PID $PID on port $PORT) stopped via port lookup."
      else
        echo "Skill Hub is not running."
      fi
    fi
    ;;

  --status|status)
    if [ -f "$PID_FILE" ]; then
      PID=$(cat "$PID_FILE")
      if kill -0 "$PID" 2>/dev/null; then
        echo "Skill Hub is running (PID $PID) on http://localhost:$PORT"
      else
        rm -f "$PID_FILE"
        echo "Skill Hub is not running — cleaned stale PID file."
      fi
    else
      PID=$(lsof -ti :$PORT 2>/dev/null || true)
      if [ -n "$PID" ]; then
        echo "Skill Hub is running (PID $PID) on http://localhost:$PORT"
      else
        echo "Skill Hub is not running."
      fi
    fi
    ;;

  *)
    # Treat argument as port number if numeric
    if [[ "${1:-}" =~ ^[0-9]+$ ]]; then
      PORT="$1"
      export SKILL_HUB_PORT="$PORT"
    fi

    # Check if already running
    if [ -f "$PID_FILE" ]; then
      OLD_PID=$(cat "$PID_FILE")
      if kill -0 "$OLD_PID" 2>/dev/null; then
        echo "Skill Hub is already running (PID $OLD_PID) on http://localhost:$PORT"
        exit 0
      else
        rm -f "$PID_FILE"
      fi
    fi

    echo "Starting Skill Hub on http://localhost:$PORT"
    # Start in background and save PID; log output to file
    nohup python3 "$MODULES_DIR/app.py" >> "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    # Give server a moment to start
    sleep 1
    # Verify it started
    if kill -0 $(cat "$PID_FILE") 2>/dev/null; then
      echo "Skill Hub started (PID $(cat "$PID_FILE")) on http://localhost:$PORT"
    else
      rm -f "$PID_FILE"
      echo "Skill Hub failed to start. Check logs for errors."
      exit 1
    fi
    ;;
esac