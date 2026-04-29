---
description: |
  Launch the Skill Hub web dashboard for browsing, searching, testing,
  and managing all Claude Code skills. Triggers: "skill hub", "skill dashboard".
---

# /skill-hub

Launch the Skill Hub web dashboard on `localhost:8765`.

```bash
bash ~/.claude/skills/skill-hub/scripts/start.sh
```

Or with custom port:

```bash
SKILL_HUB_PORT=9000 bash ~/.claude/skills/skill-hub/scripts/start.sh
```

Features:
- Home page: skill cards grid with search
- Skill detail: SKILL.md, scripts, modules, config
- Test panel: run pytest via WebSocket streaming
- Health dashboard: aggregate stats and pass rates
- Install page: dependency check and install commands
- REST API: `/api/skills`, `/api/skills/{name}`, `/api/health`