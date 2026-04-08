# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
| 1.0.0 | 2025-04-08 | Initial release with url-fetcher skill |
