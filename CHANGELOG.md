# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.0] - 2026-04-29

### Added
- ✨ **skill-hub** skill - Local web dashboard for browsing, searching, testing, and managing all Claude Code skills
  - FastAPI backend (async) + Jinja2 server-side rendering + vanilla HTML/CSS/JS
  - SQLite for skill metadata and test history
  - Auto-discover skills by scanning skills/core/*/SKILL.md and skills/external/*/SKILL.md
  - Home page: skill cards grid with name, version, layer, test count, health badge, description, search bar
  - Skill detail page: render SKILL.md, list scripts/modules, show config, version history, dependencies
  - Test panel: run pytest and stream results via WebSocket
  - Health dashboard: aggregate stats, test pass rates, dependency status
  - Install page: dynamic skills table with dependency install status, check-deps button
  - REST API: /api/skills, /api/skills/{name}, /api/skills/{name}/test, /api/health, /api/skills/{name}/check-deps
  - 300 tests (skill_discovery, database, API endpoints, HTML pages, dependency checking)
  - Server on localhost:8765, configurable via SKILL_HUB_PORT

## [1.3.0] - 2026-04-28

### Added
- ✨ **Bloomberg** skill templates (external) - Financial analysis templates for Claude Code
  - Sector Snapshot - Analyze sector trends and dynamics
  - Breaking Event - Market event impact analysis
  - Credit Strategy (Custom) - Credit market strategy framework
  - Company Snapshot, Management & Governance, Performance Tracker, Trends Analysis
- ✨ **Wind** skill placeholder (external) - Wind financial data terminal integration
- ✨ **daily-dev-pulse** skill - Personalized developer morning briefing
  - GitHub activity scanner (commits, PRs, issues, CI status via gh CLI)
  - Security/CVE checker (NVD API for tech stack vulnerabilities)
  - News aggregator (HN, Dev.to, Lobsters via public APIs)
  - Package watcher (npm + PyPI latest versions for dependencies)
  - Three output modes: terminal (ASCII charts + colors), markdown, JSON
  - Auto-generated action items from stale PRs, failing CI, security alerts
  - Configurable via ~/.quinn-skills/pulse-config.yml
- 🔧 Added github-activity and rss-fetch MCP server entries
- 🧪 **pytest** unit tests for presearch core modules
  - keyword_extractor (19 tests): extraction, stopwords, dedup, translation
  - ranking (19 tests): popularity, activity, quality, community scoring
  - translator (18 tests): Chinese detection, local dict, API fallback
  - formatter (35 tests): timestamps, stars, health indicators, GitHub/arXiv formatting
- 🔧 Reorganized skills into core/ and external/ directory structure
- 📝 Updated README with 3 skills (bilingual)
- 📝 Updated install.sh for daily-dev-pulse config setup

## [1.2.0] - 2025-04-08

### Added
- ✨ **investor-distiller** skill - Extract investment wisdom from legendary investors
  - Support for Buffett, Munger, Dalio, Soros, Druckenmiller, etc.
  - Generate investment frameworks and checklists
  - Distill investment philosophies into actionable strategies
- ✨ **macro-brief** skill - Generate macroeconomic briefs and market analysis
  - Daily/weekly brief templates
  - Key economic indicators tracking
  - Central bank policy analysis
  - Growth-inflation matrix framework
- ✨ **earnings-analyzer** skill - Analyze financial statements and earnings reports
  - Three-statement analysis (income, balance sheet, cash flow)
  - Key metrics and ratios
  - DuPont analysis
  - Industry benchmarks
- 📝 Updated README with 7 skills (bilingual)
- 📝 Updated project structure

## [1.1.0] - 2025-04-08

### Added
- ✨ **creative-prompt** skill - Generate creative prompts for writing, design, brainstorming
- ✨ **dev-joke** skill - Developer jokes and coding humor
- ✨ **code-poet** skill - Transform code into poetry
- 📝 Added skill template (`templates/SKILL_TEMPLATE.md`)
- 📝 Updated README with bilingual skill descriptions
- 📝 Updated project structure documentation

## [1.0.1] - 2025-04-08

### Added
- 🔧 LLM Agent integration (`scripts/llm_agent.py`, `scripts/llm.sh`)
- 🔧 Environment configuration (`.env.example`)
- 📝 Bilingual README (English + 中文)
- 📝 Project documentation (AGENTS.md, CLAUDE.md, CHANGELOG.md)
- 📝 Memory system (`memory/`)
- 📝 Custom commands (`.claude/commands/`)

## [1.0.0] - 2025-04-08

### Added
- ✨ Initial release of quinn-awesome-skills
- ✨ **url-fetcher** skill - Fetch any URL as clean Markdown
  - Support for X/Twitter via fxtwitter.com API (no login required)
  - Support for Instagram via fxstagram.com
  - Support for TikTok via tnktok.com
  - Support for Reddit via vxreddit.com
  - Support for Threads via fixthreads.seria.moe
  - Support for Bluesky via fxbsky.app
  - WeChat 公众号 support via Playwright
  - Feishu/Lark document support via API
  - PDF extraction (marker-pdf, pdftotext, pypdf)
  - Web search via open-webSearch (8 engines, no API key required)
  - Proxy cascade: r.jina.ai → defuddle.md → agent-fetch
- 📝 Comprehensive documentation (README, AGENTS.md, CONTRIBUTING.md)
- 🔧 MIT License

### Supported Platforms

| Platform | Method | Status |
|----------|--------|--------|
| X/Twitter | fxtwitter.com API | ✅ |
| Instagram | fxstagram.com | ✅ |
| TikTok | tnktok.com | ✅ |
| Reddit | vxreddit.com | ✅ |
| Threads | fixthreads.seria.moe | ✅ |
| Bluesky | fxbsky.app | ✅ |
| WeChat 公众号 | Playwright | ✅ |
| Feishu/Lark | API | ✅ |
| PDF | Multiple methods | ✅ |
| Web Search | open-webSearch | ✅ |

---

## Version History Summary

| Version | Date | Description |
|---------|------|-------------|
| 1.4.0 | 2026-04-29 | Add skill-hub web dashboard (FastAPI + Jinja2 + SQLite), dynamic dep checking, 300 tests |
| 1.3.0 | 2026-04-28 | Add Bloomberg/Wind external skills, pytest tests for presearch, reorganize skill dirs, daily-dev-pulse |
| 1.2.0 | 2025-04-08 | Add investor-distiller, macro-brief, earnings-analyzer (investment skills) |
| 1.1.0 | 2025-04-08 | Add creative-prompt, dev-joke, code-poet skills |
| 1.0.1 | 2025-04-08 | Add LLM Agent, environment config, bilingual README |
| 1.0.0 | 2025-04-08 | Initial release with url-fetcher skill |
