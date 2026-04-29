---
name: skill-hub
description: |
  Skill Hub web dashboard for browsing, searching, testing, and managing all
  Claude Code skills in quinn-awesome-skills. FastAPI + Jinja2 + SQLite.
  Triggers on "skill hub", "skill dashboard", "manage skills", "/skill-hub".
version: 1.0.0
author: quinnmacro
layer: core
---

# Skill Hub - Skill Management Dashboard

Local web dashboard for browsing, searching, testing, and managing Claude Code skills.

## Quick Start

```bash
# Start the server
bash ~/.claude/skills/skill-hub/scripts/start.sh

# Or with custom port
SKILL_HUB_PORT=9000 bash ~/.claude/skills/skill-hub/scripts/start.sh
```

Server runs on `localhost:8765` (configurable via `SKILL_HUB_PORT`).

## Features

1. **Home page** - Skill cards grid with name, version, layer, test count, health badge, description, pass rate, last-tested timestamp. Search bar filters by name/description. Sort by name, version, test count, health. Layer/health filter dropdowns. Re-sync skills button.
2. **Skill detail page** - Render SKILL.md content, list scripts/modules, show config, dependencies (with per-skill Check Dependencies button), version history, Quick Run Tests button for inline test execution with live output display.
3. **Test panel** - Run pytest and stream results via WebSocket.
4. **Health dashboard** - Aggregate stats, passing/failing/unknown counts, test pass rates, dependency status, CSV export.
5. **Install page** - Install commands, dependency check.
6. **REST API** - `/api/skills`, `/api/skills/{name}`, `/api/skills/{name}/test`, `/api/health`.

## REST API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/skills` | GET | List all skills (with optional search, layer, health, sort filters) |
| `/api/skills/{name}` | GET | Get skill detail by name |
| `/api/skills/{name}/test` | POST | Run tests for a skill |
| `/api/skills/{name}/versions` | GET | Get version history for a skill |
| `/api/skills/{name}/check-deps` | POST | Check dependency installation status |
| `/api/skills/export.csv` | GET | Export all skills as CSV |
| `/api/skills/resync` | POST | Re-discover skills from filesystem and sync to database |
| `/api/skills/test-all` | POST | Run tests for all skills and return aggregated results |
| `/api/health` | GET | Health dashboard data |

## Dependencies

```bash
pip install fastapi uvicorn jinja2 aiosqlite httpx websockets pytest pytest-asyncio
```

## Configuration

- `SKILL_HUB_PORT` - Server port (default: 8765)
- `SKILL_HUB_DB` - SQLite database path (default: ~/.quinn-skills/skill-hub.db)
- `SKILL_HUB_SKILLS_DIR` - Skills directory to scan (default: auto-detected from project root)

## Notes

- Auto-discovery scans `skills/core/*/SKILL.md` and `skills/external/*/SKILL.md`
- WebSocket at `/ws/test/{name}` for live test result streaming
- SQLite stores skill metadata, test run history, and version tracking
- Responsive design with mobile breakpoints, inline SVG favicon
- Version history recorded on skill version changes during sync
- Sort options: name (asc/desc), version, test_count, health (priority order)
- Skill cards show pass rate percentage and last-tested timestamp from recent test runs
- Detail page has Check Dependencies button that calls /api/skills/{name}/check-deps and shows results