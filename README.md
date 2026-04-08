# quinn-awesome-skills

> Personal collection of Claude Code skills for AI-native development workflows

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
![Skills Count](https://img.shields.io/badge/skills-1-brightgreen)

个人维护的 Claude Code skills 集合，聚焦于 URL 处理、内容抓取、Web 搜索等实用功能。

## Skills

| Skill | Description | Category |
|-------|-------------|----------|
| [url-fetcher](skills/url-fetcher/) | Fetch any URL as clean Markdown. Supports X/Twitter, WeChat 公众号, Feishu docs, PDFs, and web search. | 📄 Content Fetching |

## Installation

### Quick Install

```bash
# Clone the repository
git clone https://github.com/quinnmacro/quinn-awesome-skills.git ~/.claude/skills/quinn-awesome-skills

# Or install individual skill
git clone https://github.com/quinnmacro/quinn-awesome-skills.git /tmp/quinn-skills
cp -r /tmp/quinn-skills/skills/url-fetcher ~/.claude/skills/
```

### Manual Installation

1. Create skills directory: `mkdir -p ~/.claude/skills`
2. Copy desired skill folder to `~/.claude/skills/`
3. Skills load automatically when relevant

### Environment Configuration

Copy `.env.example` to `.env` and configure your credentials:

```bash
# Clone and configure
git clone https://github.com/quinnmacro/quinn-awesome-skills.git
cd quinn-awesome-skills
cp .env.example .env

# Edit .env with your API keys
```

**Required for**:
- **Feishu**: `FEISHU_APP_ID` + `FEISHU_APP_SECRET`
- **LLM Agent**: `INFINI_API_KEY` or `ANTHROPIC_API_KEY`

**Optional**:
- **Proxy**: `USE_PROXY=true` + `PROXY_URL`
- **Web Search**: `JINA_API_KEY` or `BRAVE_SEARCH_API_KEY`

## URL Fetcher Features

### Supported Platforms

| Platform | Method | Login Required |
|----------|--------|----------------|
| X/Twitter | fxtwitter.com API | ❌ No |
| Instagram | fxstagram.com | ❌ No |
| TikTok | tnktok.com | ❌ No |
| Reddit | vxreddit.com | ❌ No |
| Threads | fixthreads.seria.moe | ❌ No |
| Bluesky | fxbsky.app | ❌ No |
| WeChat 公众号 | Playwright | ❌ No |
| Feishu/Lark | API | ✅ App credentials |
| PDF | marker-pdf/pdftotext | ❌ No |
| General URLs | r.jina.ai / defuddle.md | ❌ No |

### Web Search

Built-in search via open-webSearch (no API key required):

```bash
# Search with default engine (DuckDuckGo)
bash ~/.claude/skills/url-fetcher/scripts/search.sh "query"

# Specify engine and limit
bash ~/.claude/skills/url-fetcher/scripts/search.sh "golang tutorial" brave 10
```

**Supported engines**: DuckDuckGo, Brave, Bing, Exa, Baidu, CSDN, Juejin, Startpage

### LLM Agent

Skills can call LLM for enhanced processing:

```bash
# Summarize content
bash scripts/llm.sh "Summarize: $(cat content.md)"

# Translate
bash scripts/llm.sh "Translate to Chinese" --system "You are a professional translator"

# JSON extraction
bash scripts/llm.sh "Extract all URLs from this text" --json
```

**Supported providers**: Infini GenStudio (default), Anthropic

## Usage Examples

```bash
# Fetch a webpage
bash ~/.claude/skills/url-fetcher/scripts/fetch.sh "https://example.com/article"

# Fetch a tweet
bash ~/.claude/skills/url-fetcher/scripts/fetch.sh "https://x.com/user/status/123456"

# Extract PDF content
bash ~/.claude/skills/url-fetcher/scripts/extract_pdf.sh "/path/to/paper.pdf"

# Web search
bash ~/.claude/skills/url-fetcher/scripts/search.sh "Claude Code skills"
```

## Requirements

### url-fetcher
- **Core**: bash, curl, python3
- **WeChat**: `pip install playwright beautifulsoup4 lxml && playwright install chromium`
- **Feishu**: `FEISHU_APP_ID` and `FEISHU_APP_SECRET` environment variables
- **PDF**: `pip install marker-pdf` (best) or `brew install poppler` (pdftotext)
- **Search**: `npx open-websearch@latest`

### LLM Agent (Optional)
- **Core**: `pip install requests`
- **Config**: Set `INFINI_API_KEY` or `ANTHROPIC_API_KEY` in `.env`

## Project Structure

```
quinn-awesome-skills/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── skills/
│   └── url-fetcher/
│       ├── SKILL.md
│       ├── scripts/
│       │   ├── fetch.sh
│       │   ├── search.sh
│       │   ├── extract_pdf.sh
│       │   ├── fetch_weixin.py
│       │   └── fetch_feishu.py
│       └── references/
│           └── methods.md
└── .github/
    └── workflows/
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Resources

- [Claude Code Skills Documentation](https://docs.claude.com/en/docs/claude-code/skills)
- [anthropics/skills](https://github.com/anthropics/skills) - Official Anthropic skills
- [obra/superpowers](https://github.com/obra/superpowers) - Battle-tested skills library
- [awesome-claude-skills](https://github.com/karanb192/awesome-claude-skills) - Community collection

## License

MIT License - see [LICENSE](LICENSE) for details.

---

**Author**: [@quinnmacro](https://github.com/quinnmacro)

**Star this repo** if you find it helpful! ⭐
