---
description: Skill Hub web dashboard — browse, search, test, and manage all skills
allowed-tools: Bash(python3 *), Bash(bash *)
---

# /skill-hub — Skill Hub Dashboard

Start the Skill Hub web application to browse, search, test, and manage all Claude Code skills.

## Usage

- `/skill-hub` — Start server on default port 8765
- `/skill-hub 9000` — Start server on custom port
- `/skill-hub --stop` — Stop running server
- `/skill-hub --status` — Check if server is running

## Workflow

1. **Start server** — Run `python3 skills/core/skill-hub/modules/app.py` with the specified port
2. **Open browser** — Show the URL (http://localhost:{port}) for the user to access
3. **Report status** — Confirm server started successfully

If `--stop` is given, find and kill the running Skill Hub process.

If `--status` is given, check if the server is running and report its URL.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SKILL_HUB_PORT` | 8765 | Server port |
| `SKILL_HUB_DB` | ~/.quinn-skills/skill-hub.db | SQLite database path |
| `SKILL_HUB_SKILLS_DIR` | auto | Skills directory to scan |

## Features

- Home page: skill cards grid with search
- Skill detail page: SKILL.md, scripts, modules, test history
- Test panel: run pytest with WebSocket streaming
- Health dashboard: aggregate stats and pass rates
- Install page: dependency check and install commands
- REST API: /api/skills, /api/skills/{name}, /api/skills/{name}/test, /api/health
