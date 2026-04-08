#!/usr/bin/env bash
# LLM Agent Helper for Skills
# Usage: llm.sh "prompt" [--system "system prompt"] [--json]
#
# Loads environment from .env and calls LLM API.
# Supports both Anthropic and Infini providers.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

python3 "$SCRIPT_DIR/llm_agent.py" "$@"
