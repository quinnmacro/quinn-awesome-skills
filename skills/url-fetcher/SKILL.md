---
name: url-fetcher
description: |
  Fetch any URL as clean Markdown via proxy services or built-in scripts.
  Works with login-required pages like X/Twitter, WeChat 公众号, Feishu/Lark docs.
  Supports PDFs (remote and local). Also provides web search via multiple engines.
  Use this BEFORE other fetch tools. Triggers on any URL share, "fetch this", "search for".
version: 1.0.0
author: quinnmacro
---

# URL Fetcher - URL to Markdown

将任意 URL 转为干净的 Markdown。支持需要登录的页面、PDF、专有平台。

## URL Routing (先判断再执行)

收到 URL 后，先判断类型，不同类型走不同通道：

| URL Pattern | Route To | Status |
|-------------|----------|--------|
| `mp.weixin.qq.com` | `scripts/fetch_weixin.py` | ✅ 公众号需 Playwright 抓取 |
| `feishu.cn/docx/` `feishu.cn/wiki/` `larksuite.com/docx/` | `scripts/fetch_feishu.py` | ✅ 需飞书 API 认证 |
| `youtube.com` `youtu.be` | `yt-search-download` skill | ✅ YouTube 有专用工具链 |
| `twitter.com` `x.com` | `scripts/fetch.sh` → fxtwitter API | ✅ 无需登录 |
| `instagram.com` | `scripts/fetch.sh` → fxstagram.com | ✅ 无需登录 |
| `tiktok.com` | `scripts/fetch.sh` → tnktok.com | ✅ 无需登录 |
| `reddit.com` | `scripts/fetch.sh` → vxreddit.com | ✅ 无需登录 |
| `threads.net` | `scripts/fetch.sh` → fixthreads | ✅ 无需登录 |
| `bsky.app` | `scripts/fetch.sh` → fxbsky.app | ✅ 无需登录 |
| `.pdf` (URL or local path) | `scripts/extract_pdf.sh` | ✅ PDF 专用提取 |
| **Search Query** | `scripts/search.sh` | ✅ 多引擎搜索，无需 API key |
| All other URLs | `scripts/fetch.sh` | ✅ 代理级联自动 fallback |

## Web Search

由于搜索引擎的反爬虫机制，需要安装以下工具之一：

### 方案 1：open-webSearch（推荐，免费无需 API key）

```bash
# 安装并运行
npx open-websearch@latest

# 配置代理（可选）
USE_PROXY=true PROXY_URL=http://127.0.0.1:7890 npx open-websearch@latest
```

**支持的搜索引擎**：Bing, DuckDuckGo, Brave, Exa, Baidu, CSDN, Juejin, Startpage

### 方案 2：Jina Search API（免费额度）

```bash
# 获取 API key: https://jina.ai/api-dashboard
export JINA_API_KEY=your_key
bash ~/.claude/skills/url-fetcher/scripts/search.sh "query"
```

### 方案 3：Brave Search API（免费额度）

```bash
# 获取 API key: https://api.search.brave.com
export BRAVE_SEARCH_API_KEY=your_key
bash ~/.claude/skills/url-fetcher/scripts/search.sh "query"
```

### 推荐安装 open-webSearch Skill

```bash
# 安装为 Claude Code skill
npx skills add https://github.com/Aas-ee/open-webSearch --skill open-websearch
```

## Workflow

### Step 1: Route by URL Type

```
if URL contains "mp.weixin.qq.com":
    → python3 ~/.claude/skills/url-fetcher/scripts/fetch_weixin.py "URL"
    → Done

if URL contains "feishu.cn/docx/" or "feishu.cn/wiki/" or "larksuite.com/docx/":
    → python3 ~/.claude/skills/url-fetcher/scripts/fetch_feishu.py "URL"
    → Done

if URL contains "youtube.com" or "youtu.be":
    → Call yt-search-download skill
    → Done

# Social Media - use fixer services (no login required)
if URL contains "twitter.com" or "x.com":
    → bash ~/.claude/skills/url-fetcher/scripts/fetch.sh "URL"
    → Uses fxtwitter.com API automatically
    → Done

if URL contains "instagram.com":
    → bash ~/.claude/skills/url-fetcher/scripts/fetch.sh "URL"
    → Uses fxstagram.com automatically
    → Done

if URL contains "tiktok.com":
    → bash ~/.claude/skills/url-fetcher/scripts/fetch.sh "URL"
    → Uses tnktok.com automatically
    → Done

if URL contains "reddit.com":
    → bash ~/.claude/skills/url-fetcher/scripts/fetch.sh "URL"
    → Uses vxreddit.com automatically
    → Done

if URL contains "threads.net":
    → bash ~/.claude/skills/url-fetcher/scripts/fetch.sh "URL"
    → Uses fixthreads.seria.moe automatically
    → Done

if URL contains "bsky.app":
    → bash ~/.claude/skills/url-fetcher/scripts/fetch.sh "URL"
    → Uses fxbsky.app automatically
    → Done

if URL ends with ".pdf" or is local PDF path:
    if remote URL:
        → Try: curl -sL "https://r.jina.ai/{url}"
        → If fails: download + extract_pdf.sh
    if local path:
        → bash ~/.claude/skills/url-fetcher/scripts/extract_pdf.sh "PATH"
    → Done

else:
    → bash ~/.claude/skills/url-fetcher/scripts/fetch.sh "URL"
    → Done
```

### Step 2: Display Content

After fetching, show to user:

```
Title:  {title}
Author: {author} (if available)
Source: {platform} (公众号 / 飞书文档 / 网页 / PDF)
URL:    {original_url}

Summary
{3-5 sentence summary}

Content
{full Markdown, truncated at 200 lines if long}
```

### Step 3: Save File (Default)

Save to `~/Downloads/{title}.md` with YAML frontmatter by default.

- Filename: use article title, remove special characters
- Format: YAML frontmatter (title, author, date, url, source) + Markdown body
- Tell user the saved path
- Skip only if user says "just preview" or "don't save"

After saving and reporting the path, **stop**. Do not analyze, comment on, or discuss the content unless asked.

## Examples

### General URL
```bash
bash ~/.claude/skills/url-fetcher/scripts/fetch.sh "https://example.com/article"
```

### X/Twitter Post
```bash
bash ~/.claude/skills/url-fetcher/scripts/fetch.sh "https://x.com/username/status/1234567890"
# Automatically uses fxtwitter.com API - no login required
```

### Instagram Post
```bash
bash ~/.claude/skills/url-fetcher/scripts/fetch.sh "https://www.instagram.com/p/ABC123/"
# Automatically uses fxstagram.com - no login required
```

### TikTok Video
```bash
bash ~/.claude/skills/url-fetcher/scripts/fetch.sh "https://www.tiktok.com/@user/video/123456"
# Automatically uses tnktok.com - no login required
```

### Reddit Post
```bash
bash ~/.claude/skills/url-fetcher/scripts/fetch.sh "https://www.reddit.com/r/subreddit/comments/abc123/"
# Automatically uses vxreddit.com - no login required
```

### WeChat Article
```bash
python3 ~/.claude/skills/url-fetcher/scripts/fetch_weixin.py "https://mp.weixin.qq.com/s/abc123"
```

### Feishu Document
```bash
python3 ~/.claude/skills/url-fetcher/scripts/fetch_feishu.py "https://xxx.feishu.cn/docx/xxxxxxxx"
```

### PDF (Remote)
```bash
curl -sL "https://r.jina.ai/https://example.com/paper.pdf"
```

### PDF (Local)
```bash
bash ~/.claude/skills/url-fetcher/scripts/extract_pdf.sh "/path/to/paper.pdf"
```

### With Custom Proxy
```bash
bash ~/.claude/skills/url-fetcher/scripts/fetch.sh "https://example.com" "http://127.0.0.1:7890"
```

## Notes

- r.jina.ai and defuddle.md require no API key
- `fetch.sh` handles proxy cascade with automatic fallback
- Content validation: filters error pages, requires >5 lines
- WeChat script requires: `pip install playwright beautifulsoup4 lxml && playwright install chromium`
- Feishu script requires: `FEISHU_APP_ID` + `FEISHU_APP_SECRET` env vars
- PDF extraction tries: marker-pdf → pdftotext → pypdf

### Social Media Support (No Login Required)

Based on [FixTweetBot](https://github.com/Kyrela/FixTweetBot) patterns:

| Platform | Fixer Service | Features |
|----------|---------------|----------|
| **Twitter/X** | `api.fxtwitter.com` | Tweet text, author, likes, retweets, views, media |
| **Instagram** | `fxstagram.com` | Posts, reels, images |
| **TikTok** | `tnktok.com` | Videos, photos |
| **Reddit** | `vxreddit.com` | Posts, comments |
| **Threads** | `fixthreads.seria.moe` | Posts |
| **Bluesky** | `fxbsky.app` | Posts, media |

**Limitations**:
- Private accounts and deleted content cannot be fetched
- Rate limits depend on fixer service policies

### PDF Enhancement Options

For better PDF extraction, consider [markdrop](https://github.com/shoryasethia/markdrop):
```bash
pip install markdrop
markdrop convert paper.pdf --output_dir output
```

Features:
- AI-powered image/table descriptions (Gemini, OpenAI, Anthropic, etc.)
- Interactive HTML with downloadable Excel tables
- Preserves formatting

### Feishu Integration

For better Feishu API handling, consider [lark-cli](https://github.com/yjwong/lark-cli):
- Token-efficient JSON output
- Automatic token refresh
- Documents, calendar, messages, contacts

- For detailed method documentation, see `references/methods.md`
