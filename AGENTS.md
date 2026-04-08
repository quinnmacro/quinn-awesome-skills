# AGENTS.md

This file provides context for AI agents working with this skills collection.

## Project Overview

**quinn-awesome-skills** is a personal collection of Claude Code skills for AI-native development workflows. It focuses on URL processing, content fetching, web search, and practical automation tasks.

- **Author**: Quinn Liu ([@quinnmacro](https://github.com/quinnmacro))
- **Purpose**: Reusable skills for Claude Code CLI
- **Primary Skill**: `url-fetcher` - Fetch any URL as clean Markdown

## Project Structure

```
quinn-awesome-skills/
├── README.md              # Project documentation and skills list
├── AGENTS.md              # This file - context for AI agents
├── CLAUDE.md              # Claude Code project configuration
├── CHANGELOG.md           # Version history
├── CONTRIBUTING.md        # Contribution guidelines
├── LICENSE                # MIT License
├── .gitignore             # Git ignore rules
├── skills/                # Individual skill directories
│   └── url-fetcher/
│       ├── SKILL.md       # Skill definition (required)
│       ├── scripts/       # Executable scripts
│       └── references/    # Documentation
├── memory/                # Project memory (git-tracked)
│   └── MEMORY.md          # Memory index
└── .claude/               # Claude Code configuration
    └── commands/          # Custom slash commands
```

## Skill Development Guidelines

### Adding a New Skill

1. Create directory: `skills/your-skill-name/`
2. Add `SKILL.md` with YAML frontmatter:

```markdown
---
name: your-skill-name
description: |
  Clear description with trigger phrases.
version: 1.0.0
author: quinnmacro
---

# Skill Title

Instructions for Claude...
```

3. Add scripts in `scripts/` subdirectory
4. Update README.md skills table
5. Update CHANGELOG.md

### SKILL.md Best Practices

- **Clear triggers**: Include phrases that should activate the skill
- **Step-by-step workflow**: Claude follows structured instructions better
- **Code examples**: Show exactly how to run scripts
- **Error handling**: Document what to do when things fail

### Script Best Practices

```bash
#!/usr/bin/env bash
set -euo pipefail

# Clear usage message
QUERY="${1:?Usage: script.sh <query>}"

# Graceful error handling
if ! command -v required_tool &>/dev/null; then
    echo "Error: required_tool not installed" >&2
    exit 1
fi
```

## Key Commands

```bash
# Test a skill locally
bash skills/url-fetcher/scripts/fetch.sh "https://example.com"

# Web search
bash skills/url-fetcher/scripts/search.sh "query" duckduckgo 5

# Git workflow
git add . && git commit -m "✨ Add new skill"
git push origin main
```

## Dependencies

### url-fetcher
- **Core**: bash, curl, python3
- **WeChat**: `pip install playwright beautifulsoup4 lxml && playwright install chromium`
- **Feishu**: `FEISHU_APP_ID` + `FEISHU_APP_SECRET` environment variables
- **PDF**: `pip install marker-pdf` (best) or `brew install poppler`
- **Search**: `npx open-websearch@latest`

## Commit Conventions

Use gitmoji-style commits:

| Emoji | Meaning |
|-------|---------|
| ✨ | New feature |
| 🐛 | Bug fix |
| 📝 | Documentation |
| ♻️ | Refactor |
| ✅ | Tests |
| 🔧 | Configuration |

## Related Documentation

- [README.md](./README.md) - User documentation
- [CONTRIBUTING.md](./CONTRIBUTING.md) - Contribution guidelines
- [CHANGELOG.md](./CHANGELOG.md) - Version history
