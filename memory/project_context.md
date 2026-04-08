---
name: project-context
description: Overall context and goals for quinn-awesome-skills project
type: project
---

# quinn-awesome-skills Project Context

## Purpose
Personal collection of Claude Code skills for AI-native development workflows. Focus on practical automation tasks.

## Current Focus
- Building out url-fetcher as the primary skill
- Supporting Chinese platforms (WeChat 公众号, Feishu)
- Web search without API keys

## Target Audience
- Developer using Claude Code CLI
- Need URL-to-Markdown conversion
- Work with Chinese platforms
- Prefer free/open-source solutions

## Design Decisions
- **No API keys required** where possible (use open-webSearch, fixer services)
- **Proxy cascade** for reliability (r.jina.ai → defuddle.md → fallback)
- **Platform-specific scripts** for complex cases (WeChat, Feishu)

## Future Skills Ideas
- job-search-hunter (LinkedIn, Boss直聘 job scraping)
- document-summarizer (PDF, DOCX summarization)
- code-reviewer (automated code review patterns)

## References
- [Claude Code Skills Docs](https://docs.claude.com/en/docs/claude-code/skills)
- [awesome-claude-skills](https://github.com/karanb192/awesome-claude-skills)
- [obra/superpowers](https://github.com/obra/superpowers)
