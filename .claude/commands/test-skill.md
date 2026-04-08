---
allowed-tools: Bash(skills/*/scripts/*:*), Bash(bash:*)
description: Test a skill by running its scripts
---

## Context

- Available skills: !`ls skills/`

## Your Task

1. Ask the user which skill to test
2. Ask for test input (URL, query, etc.)
3. Run the appropriate script
4. Report results

Example:
```bash
bash skills/url-fetcher/scripts/fetch.sh "https://example.com"
bash skills/url-fetcher/scripts/search.sh "query" duckduckgo 5
```
