---
name: daily-dev-pulse
description: |
  Generate a personalized developer morning briefing covering GitHub activity,
  package updates, security alerts, trending dev news, and actionable todos.
  Auto-triggers on morning greetings ("good morning", "start my day"),
  time-based context (before 10am), or explicit /daily-dev-pulse command.
  Integrates with url-fetcher (fallback content extraction) and presearch
  (trend discovery) skills for enhanced data collection.
version: 1.0.0
author: quinnmacro
layer: core
---

# Daily Dev Pulse - 开发者早报

Personalized morning briefing for developers. One command, full picture of your dev world.

## Trigger Phrases / 触发词

- English: "good morning", "morning brief", "dev pulse", "daily briefing", "start my day"
- 中文: "早上好", "早报", "开发日报", "每日简报"
- Time-based: auto-suggests before 10am local time

## Workflow

### Step 1: Load Configuration

Read config from `~/.quinn-skills/pulse-config.yml`. If missing, use defaults from `config-example.yml`.

```bash
# Config location
~/.quinn-skills/pulse-config.yml
```

Default config covers:
- Repos: quinnpm, SanctionList, quinn-awesome-skills, quinnweb, gnhf, weather-cli
- Tech stack: Python 3.13, FastAPI, Next.js, SQLite, LangGraph
- Output format: terminal (default), markdown, json
- News sources: HN, Dev.to, Lobsters

### Step 2: Collect Data

Run the orchestration script to gather all data sources:

```bash
bash ~/.claude/skills/daily-dev-pulse/scripts/daily-dev-pulse.sh
```

This script orchestrates:
1. **GitHub Scanner** - `python3 ~/.claude/skills/daily-dev-pulse/modules/github_scanner.py`
   - Uses `gh` CLI to scan repos for: recent commits, open PRs, open issues, CI status
   - Output: JSON with per-repo activity summary
2. **Security Checker** - `python3 ~/.claude/skills/daily-dev-pulse/modules/security_checker.py`
   - Checks CVE databases for configured tech stack
   - Output: JSON with security alerts (severity, CVE ID, description)
3. **News Aggregator** - `python3 ~/.claude/skills/daily-dev-pulse/modules/news_aggregator.py`
   - Fetches HN top stories, Dev.to trending, Lobsters
   - Uses url-fetcher scripts as fallback when direct API fails for a source
   - Output: JSON with headlines and links
4. **Package Watcher** - `python3 ~/.claude/skills/daily-dev-pulse/modules/package_watcher.py`
   - Checks npm and PyPI for updates to dependency packages
   - Uses presearch skill for trend discovery on tech stack frameworks
   - Output: JSON with available updates and trends

### Step 3: Format Output

Pipe collected JSON data to the formatter:

```bash
python3 ~/.claude/skills/daily-dev-pulse/scripts/pulse_formatter.py --format terminal < data.json
# Or: --format md, --format json
```

Output modes:
- **terminal**: Rich console with ASCII bar charts, colored sections, emoji indicators
- **md**: Structured sections for Claude consumption (default for skill context)
- **json**: Raw structured data for programmatic use

### Step 4: Generate Action Items

The formatter automatically creates a todo section based on:
- Stale PRs (open > 3 days)
- Failing CI runs
- Unresolved issues assigned to you
- Available package updates with security relevance

## Output Format

### Terminal Mode Example

```
╔══════════════════════════════════════════════╗
║   🌅 DAILY DEV PULSE — 2025-04-28          ║
╚══════════════════════════════════════════════╝

📊 GitHub Activity (Last 7 Days)
  quinn-awesome-skills ████████ 8 commits
  gnhf                 █████    5 commits
  weather-cli          ██       2 commits
  quinnpm              ▏        1 commit

🔍 Open PRs & Issues
  ┌──────────────────┬────────┬──────────┐
  │ Repo             │ Type   │ Title    │
  ├──────────────────┼────────┼──────────┤
  │ quinn-awesome-skills │ PR  │ Add skill │
  │ gnhf             │ Issue │ Bug fix  │
  └──────────────────┴────────┴──────────┘

🛡️ Security Alerts
  ⚠️ CVE-2025-XXXX — FastAPI (High)
  📋 CVE-2025-YYYY — SQLite (Medium)

📰 Trending Dev News (HN Top 10)
  1. "New Python 3.13 features explained"
  2. "Why SQLite is the perfect embedded DB"

✅ Action Items
  → Review stale PR #42 on quinn-awesome-skills
  → Fix failing CI on gnhf branch
  → Update FastAPI to 0.115.0 (security patch)
```

### Markdown Mode

Structured with `##` sections, tables, and checklist items. Used when Claude needs to consume and relay the briefing.

### JSON Mode

```json
{
  "date": "2025-04-28",
  "github": { "repos": [...], "commits": [...], "prs": [...], "issues": [...] },
  "security": { "alerts": [...] },
  "news": { "headlines": [...] },
  "packages": { "updates": [...] },
  "action_items": [...]
}
```

## Arguments

| Arg | Values | Description |
|-----|--------|-------------|
| `--repos` | `all`, `quinnpm,SanctionList,...` | Which repos to scan (default: all from config) |
| `--focus` | `security`, `news`, `activity`, `all` | Focus area (default: all) |
| `--format` | `terminal`, `md`, `json` | Output format (default: terminal) |
| `--days` | `1`, `7`, `30` | Activity lookback period (default: 7) |
| `--config` | `/path/to/config.yml` | Custom config file path (default: ~/.quinn-skills/pulse-config.yml) |

## Dependencies

- **gh CLI** — GitHub API (`brew install gh` or see https://cli.github.com)
- **python3** — Script execution
- **PyYAML** — Config file parsing (`pip install pyyaml`; only required when using custom config file — defaults work without it)
- **url-fetcher skill** — Fallback content extraction when direct API fails for news sources
- **presearch skill** — Optional trend discovery for tech stack frameworks

## Configuration

Copy `config-example.yml` to `~/.quinn-skills/pulse-config.yml` and customize:

```yaml
repos:
  - name: quinn-awesome-skills
    owner: quinnmacro
  - name: gnhf
    owner: quinnmacro

tech_stack:
  python: "3.13"
  frameworks: [FastAPI, Next.js]
  databases: [SQLite]
  libraries: [LangGraph]

dependencies:
  npm: [next, react, tailwindcss]
  pypi: [fastapi, uvicorn, langgraph, sqlalchemy, pyyaml, requests]

preferences:
  news_sources: [hn, devto, lobsters]
  format: terminal
  lookback_days: 7
  security_lookback_days: 30
  stale_pr_days: 3
  nvd_rate_limit: 6
  max_issues_per_repo: 3
```

## Notes

- If `gh` is not authenticated, GitHub sections will be skipped with a warning
- CVE checks use public NVD API (no key required, rate-limited to 5 req/min without key)
- News aggregation uses url-fetcher scripts as fallback when direct API (HN, Dev.to, Lobsters) returns no data
- Package trend discovery uses presearch skill to find alternatives/trends for tech stack frameworks
- Config is optional — defaults cover the author's repos and tech stack

## Related Skills

- url-fetcher — Used as fallback for news content extraction when direct API fails
- presearch — Used for discovering trending package alternatives for tech stack frameworks