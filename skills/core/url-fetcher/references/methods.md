# Fetch Methods Reference

## Web Search (无需 API Key)

### 使用内置脚本

```bash
bash ~/.claude/skills/qiaomu-markdown-proxy/scripts/search.sh "query" [engine] [limit]
```

**支持的搜索引擎**：duckduckgo, brave, bing, exa, baidu, csdn, juejin, startpage

### 推荐：安装 open-webSearch

[open-webSearch](https://github.com/Aas-ee/open-webSearch) (937 stars) 提供更好的搜索体验：

```bash
# 一键运行（MCP server）
npx open-websearch@latest

# 带代理
USE_PROXY=true PROXY_URL=http://127.0.0.1:7890 npx open-websearch@latest

# 安装为 skill
npx skills add https://github.com/Aas-ee/open-webSearch --skill open-websearch
```

**特性**：
- 8+ 搜索引擎
- 无需 API key
- 支持代理
- MCP server + CLI + 本地守护进程

### Jina AI Search API

如果设置了 `JINA_API_KEY` 环境变量，search.sh 会自动使用 Jina Search API：

```bash
export JINA_API_KEY=your_key
bash ~/.claude/skills/qiaomu-markdown-proxy/scripts/search.sh "query"
```

获取 API key：https://jina.ai/api-dashboard

### Brave Search Skills

[Brave 官方 skills](https://github.com/brave/brave-search-skills) 提供多种搜索类型：

```bash
# 安装
mkdir -p ~/.claude/skills && curl -sL https://github.com/brave/brave-search-skills/archive/main.tar.gz | tar xz -C ~/.claude/skills --strip-components=2 brave-search-skills-main/skills

# 配置 API key
# 添加到 ~/.claude/settings.json:
# {"env": {"BRAVE_SEARCH_API_KEY": "your-key"}}
```

**支持的搜索类型**：
- web-search - 网页搜索
- images-search - 图片搜索
- news-search - 新闻搜索
- videos-search - 视频搜索
- llm-context - LLM 优化的搜索结果

## Proxy Cascade (General URLs)

Use `scripts/fetch.sh` for automatic proxy cascade with fallback. Try in order until success:

### 1. r.jina.ai

```bash
bash ~/.claude/skills/qiaomu-markdown-proxy/scripts/fetch.sh "https://example.com"
```

Wide coverage, preserves image links. Try this first.

### 2. defuddle.md

Automatically tried by `fetch.sh` if r.jina.ai fails. Cleaner output with YAML frontmatter.

### 3. agent-fetch

Last resort local tool, automatically tried if both proxies fail.

### With Custom Proxy

```bash
bash ~/.claude/skills/qiaomu-markdown-proxy/scripts/fetch.sh "https://example.com" "http://127.0.0.1:7890"
```

## Social Media (No Login Required)

Based on [FixTweetBot](https://github.com/Kyrela/FixTweetBot) patterns. All fixer services require no authentication.

### Twitter/X

```bash
bash ~/.claude/skills/qiaomu-markdown-proxy/scripts/fetch.sh "https://x.com/username/status/123456"
```

**API**: `api.fxtwitter.com`
**Extracts**: Tweet text, author info, likes, retweets, views, media links
**Limitations**: Private accounts and deleted tweets cannot be fetched

### Instagram

```bash
bash ~/.claude/skills/qiaomu-markdown-proxy/scripts/fetch.sh "https://www.instagram.com/p/ABC123/"
```

**Service**: `fxstagram.com`
**Supported**: Posts, reels, images

### TikTok

```bash
bash ~/.claude/skills/qiaomu-markdown-proxy/scripts/fetch.sh "https://www.tiktok.com/@user/video/123456"
```

**Service**: `tnktok.com` (a.tnktok.com for embeds, d.tnktok.com for direct media)
**Supported**: Videos, photos

### Reddit

```bash
bash ~/.claude/skills/qiaomu-markdown-proxy/scripts/fetch.sh "https://www.reddit.com/r/subreddit/comments/abc123/"
```

**Service**: `vxreddit.com`
**Supported**: Posts, comments, galleries

### Threads

```bash
bash ~/.claude/skills/qiaomu-markdown-proxy/scripts/fetch.sh "https://www.threads.net/@username/post/ABC123"
```

**Service**: `fixthreads.seria.moe`

### Bluesky

```bash
bash ~/.claude/skills/qiaomu-markdown-proxy/scripts/fetch.sh "https://bsky.app/profile/user.bsky.social/post/abc123"
```

**Service**: `fxbsky.app`
**Views**: Normal, gallery (g.), text-only (t.), direct-media (d.)

### Bilibili

```bash
bash ~/.claude/skills/qiaomu-markdown-proxy/scripts/fetch.sh "https://www.bilibili.com/video/BV1234567890"
```

**Service**: `vxbilibili.com`

## PDF to Markdown

### Remote PDF URL

r.jina.ai handles PDF URLs directly:

```bash
curl -sL "https://r.jina.ai/https://example.com/paper.pdf"
```

If that fails, download and extract locally:

```bash
curl -sL "https://example.com/paper.pdf" -o /tmp/input.pdf
bash ~/.claude/skills/qiaomu-markdown-proxy/scripts/extract_pdf.sh /tmp/input.pdf
```

### Local PDF File

```bash
bash ~/.claude/skills/qiaomu-markdown-proxy/scripts/extract_pdf.sh /path/to/file.pdf
```

The script tries three methods in order:

1. **marker-pdf** (best quality, requires: `pip install marker-pdf`)
   - Best for papers, tables, complex layouts
   - Preserves formatting and structure

2. **pdftotext** (fast, requires: `brew install poppler`)
   - Good for text-heavy PDFs
   - Fast extraction with layout preservation

3. **pypdf** (no-dependency fallback, requires: `pip install pypdf`)
   - Works everywhere Python is available
   - Basic text extraction

### Enhanced PDF Extraction (Optional)

For better results with AI-powered image/table descriptions, use [markdrop](https://github.com/shoryasethia/markdrop):

```bash
pip install markdrop
markdrop convert paper.pdf --output_dir output --add_tables
markdrop describe output/paper.md --ai_provider gemini
```

**Features**:
- AI-powered image descriptions (Gemini, OpenAI, Anthropic, Groq, etc.)
- Table detection with Excel export
- Interactive HTML output

## WeChat Public Account (公众号)

Use the proxy cascade first (r.jina.ai / defuddle.md). Works for most articles without extra tools.

If proxies are blocked, use the built-in Playwright script as last resort:

```bash
python3 ~/.claude/skills/qiaomu-markdown-proxy/scripts/fetch_weixin.py "https://mp.weixin.qq.com/s/abc123"
```

**Requirements** (one-time setup, ~300 MB):
```bash
pip install playwright beautifulsoup4 lxml
playwright install chromium
```

**Output**: YAML frontmatter (title, author, date, url) + Markdown body

**JSON output**:
```bash
python3 ~/.claude/skills/qiaomu-markdown-proxy/scripts/fetch_weixin.py "URL" --json
```

### Batch Processing (Optional)

For batch scraping with Notion integration, see [wechat-mp-batch-scraper](https://github.com/haosizheng/wechat-mp-batch-scraper):

```bash
git clone https://github.com/haosizheng/wechat-mp-batch-scraper
cd wechat-mp-batch-scraper
pip install playwright requests Pillow
playwright install
```

## Feishu / Lark Document

Built-in API script for Feishu documents. Requires app credentials:

```bash
export FEISHU_APP_ID=your_app_id
export FEISHU_APP_SECRET=your_app_secret
python3 ~/.claude/skills/qiaomu-markdown-proxy/scripts/fetch_feishu.py "https://xxx.feishu.cn/docx/xxxxxxxx"
```

**Supported types**:
- `docx` - New-style documents
- `doc` - Legacy documents
- `wiki` - Wiki pages (auto-resolves to actual document)

**Required permissions**: `docx:document:readonly`, `wiki:wiki:readonly`

**Output**: YAML frontmatter (title, document_id, url) + Markdown body

**JSON output**:
```bash
python3 ~/.claude/skills/qiaomu-markdown-proxy/scripts/fetch_feishu.py "URL" --json
```

### Alternative: lark-cli (Optional)

For token-efficient API access, use [lark-cli](https://github.com/yjwong/lark-cli):

```bash
# Install
go install github.com/yjwong/lark-cli@latest

# Read document as markdown
lark doc read <document_token>
```

**Features**:
- Compact JSON output (2-3x smaller than raw API)
- Automatic token refresh
- Calendar, contacts, messages support

## YouTube Videos

Use the dedicated `yt-search-download` skill for YouTube content. It handles:
- Video download
- Subtitle extraction
- Transcript generation

Do not use qiaomu-markdown-proxy for YouTube URLs.

## Content Validation

The `fetch.sh` script validates content before returning:

- Must have more than 5 lines
- Filters out common error pages:
  - "Don't miss what's happening" (Twitter login wall)
  - "Access Denied"
  - "404 Not Found"

If validation fails, automatically tries the next method.

## Best Practices from GitHub

### FixTweetBot Patterns

[FixTweetBot](https://github.com/Kyrela/FixTweetBot) (197 stars) demonstrates:

1. **URL Normalization**: Convert domain to fixer service
2. **Subdomain Views**: Different subdomains for different views
   - Normal: `fxtwitter.com`
   - Gallery: `g.fxtwitter.com`
   - Text-only: `t.fxtwitter.com`
   - Direct media: `d.fxtwitter.com`
3. **Regex Routing**: Match URL patterns with named groups
4. **Fallback Chain**: Try fixer service → original → error

### markdrop Patterns

[markdrop](https://github.com/shoryasethia/markdrop) (198 stars) demonstrates:

1. **AI Provider Abstraction**: Support multiple LLM providers
2. **Structured Output**: YAML frontmatter + Markdown body
3. **Table Extraction**: Microsoft Table Transformer
4. **Image XRef IDs**: Track images by PDF internal IDs

### lark-cli Patterns

[lark-cli](https://github.com/yjwong/lark-cli) (41 stars) demonstrates:

1. **Compact Output**: Return minimal JSON for AI consumption
2. **Markdown Conversion**: Convert API responses to Markdown
3. **Selective Queries**: Fetch only what's needed
