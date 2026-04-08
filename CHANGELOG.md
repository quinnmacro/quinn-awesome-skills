# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-04-08

### Added
- ✨ **creative-prompt** skill - Generate creative prompts for writing, design, brainstorming
  - Writing prompts (story starters, character ideas, plot twists)
  - Design prompts (logo, poster, UI inspiration)
  - Brainstorm prompts using SCAMPER technique
- ✨ **dev-joke** skill - Developer jokes and coding humor
  - Classic programming jokes
  - Debug life humor
  - Tech stack jokes
  - Git humor
  - Support for frustration relief during debugging
- ✨ **code-poet** skill - Transform code into poetry
  - Haiku (5-7-5)
  - Free verse
  - Sonnet
  - Chinese classical poetry (唐诗宋词)
  - Poetic code explanation
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
| 1.1.0 | 2025-04-08 | Add creative-prompt, dev-joke, code-poet skills |
| 1.0.1 | 2025-04-08 | Add LLM Agent, environment config, bilingual README |
| 1.0.0 | 2025-04-08 | Initial release with url-fetcher skill |
