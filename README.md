# quinn-awesome-skills

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
![Skills Count](https://img.shields.io/badge/skills-8-brightgreen)
![Commands](https://img.shields.io/badge/commands-8-blue)
![MCP Ready](https://img.shields.io/badge/MCP-ready-purple)
![Claude Code](https://img.shields.io/badge/Claude_Code-compatible-orange)

> **Personal collection of Claude Code skills for AI-native development workflows**
>
> 个人维护的 Claude Code skills 集合，采用 Skills/Commands/Connectors 三层架构

[English](#-english) | [中文](#-中文)

---

## Why quinn-awesome-skills?

Traditional AI assistants require repetitive prompting for domain-specific tasks. **Skills change this**:

| Without Skills | With Skills |
|----------------|-------------|
| Every task needs detailed instructions | Domain knowledge is encoded once |
| Inconsistent output quality | Professional, standardized workflows |
| Manual data fetching from multiple sources | MCP connectors pull live data |
| No learning across sessions | Skills persist and improve |
| Hours explaining "how we do analysis" | One `/command` triggers best practices |

**quinn-awesome-skills** bundles domain expertise, workflow automation, and data connections into a single installable package — so Claude works like it was built for your workflow.

---

## Architecture

```
quinn-awesome-skills/
├── skills/                    # Skills (auto-triggered domain knowledge)
│   ├── core/                  # Core utilities
│   │   ├── url-fetcher/       # URL → Markdown converter
│   │   └── presearch/         # Developer resource search
│   ├── investment/            # Investment analysis
│   │   ├── investor-distiller/    # Investment wisdom extraction
│   │   ├── macro-brief/           # Macroeconomic analysis
│   │   └── earnings-analyzer/     # Financial statement analysis
│   └── creative/              # Creative tools
│       ├── creative-prompt/       # Ideation assistant
│       ├── dev-joke/              # Developer humor
│       └── code-poet/             # Code poetry
├── commands/                  # Slash commands (explicit triggers)
│   ├── url-fetcher.md
│   ├── presearch.md
│   └── ...
├── connectors/                # MCP data connectors
│   └── mcp-servers.json       # Data provider configurations
└── scripts/                   # Shared utilities
    ├── llm_agent.py           # LLM integration
    └── llm.sh                 # Shell wrapper
```

### Three-Layer Architecture

| Layer | Purpose | Trigger |
|-------|---------|---------|
| **Skills** | Domain expertise, workflows, best practices | Auto-triggered when relevant |
| **Commands** | Explicit actions via `/command` | Manual invocation |
| **Connectors** | MCP data connections | Skills/Commands use them |

This separation means:
- Skills encode *knowledge* (how to do DCF analysis)
- Commands provide *entry points* (`/dcf Apple`)
- Connectors provide *data* (financial statements via API)

---

## English

### Skills Overview

#### Core Skills

| Skill | Description | Command | Status |
|-------|-------------|---------|--------|
| [url-fetcher](skills/core/url-fetcher/) | Fetch any URL as clean Markdown. WeChat, Feishu, PDF, Web search. | `/url-fetcher` | ✅ Production |
| [presearch](skills/core/presearch/) | Search developer resources. GitHub, npm, PyPI, Docker Hub, arXiv. | `/presearch` | ✅ Production |

#### Investment Skills

| Skill | Description | Command | Status |
|-------|-------------|---------|--------|
| [investor-distiller](skills/investment/investor-distiller/) | Extract investment wisdom from legendary investors. | `/investor-distiller` | ✅ Production |
| [macro-brief](skills/investment/macro-brief/) | Generate macroeconomic briefs and market analysis. | `/macro-brief` | ✅ Production |
| [earnings-analyzer](skills/investment/earnings-analyzer/) | Analyze financial statements and earnings reports. | `/earnings-analyzer` | ✅ Production |

#### Creative Skills

| Skill | Description | Command | Status |
|-------|-------------|---------|--------|
| [creative-prompt](skills/creative/creative-prompt/) | Generate creative prompts for writing and design. | `/creative-prompt` | ✅ Production |
| [dev-joke](skills/creative/dev-joke/) | Developer jokes and coding humor. | `/dev-joke` | ✅ Production |
| [code-poet](skills/creative/code-poet/) | Transform code into poetry. | `/code-poet` | ✅ Production |

### Detailed Features

#### URL Fetcher — Universal Content Extraction

Convert any URL to clean Markdown with zero configuration:

| Platform | Method | Features |
|----------|--------|----------|
| **WeChat 公众号** | Playwright scraping | Full article, preserves formatting |
| **Feishu/Lark** | Official API | Documents, wikis, spreadsheets |
| **X/Twitter** | fxtwitter.com | Tweets, threads, media |
| **Instagram** | fxstagram.com | Posts, reels, images |
| **TikTok** | tnktok.com | Videos, photos |
| **Reddit** | vxreddit.com | Posts, comments |
| **Threads** | fixthreads | Posts |
| **Bluesky** | fxbsky.app | Posts, media |
| **PDF** | marker-pdf / pdftotext | Remote URLs and local files |
| **Web Search** | open-websearch | 8 engines, no API key required |

```bash
/url-fetcher https://mp.weixin.qq.com/s/abc123    # WeChat article
/url-fetcher https://x.com/user/status/123        # Twitter post
/url-fetcher https://arxiv.org/pdf/2401.12345     # Academic paper
/url-fetcher "React best practices"               # Web search
```

#### Presearch — Developer Resource Intelligence

Before building, search existing solutions:

| Source | Data Retrieved | Health Checks |
|--------|----------------|---------------|
| **GitHub** | Stars, forks, issues, last commit | Activity score, maintenance status |
| **npm** | Downloads, dependencies, versions | Security audit, deprecation |
| **PyPI** | Downloads, dependencies, versions | Security audit |
| **Docker Hub** | Pulls, stars, last updated | Official status |
| **arXiv** | Papers, citations, authors | Related papers |

**Output Formats**: `default` | `emoji` | `meme` | `poetry`

```bash
/presearch "Python web framework"        # Find best Python web frameworks
/presearch "React state management" emoji # Emoji-style output
/presearch "machine learning library" poetry # Poetic description
```

#### Investment Skills — Professional Financial Analysis

| Skill | Use Case | Output |
|-------|----------|--------|
| **investor-distiller** | Extract mental models from Buffett, Munger, Dalio | Investment frameworks, decision trees |
| **macro-brief** | Daily/weekly economic briefings | Economic indicators, market trends |
| **earnings-analyzer** | Company financial analysis | Key metrics, trends, investment insights |

```bash
/investor-distiller 巴菲特              # Buffett's investment philosophy
/macro-brief weekly                     # Weekly macro summary
/earnings-analyzer Apple 2024Q4         # Apple earnings analysis
```

### MCP Data Connectors

All connectors use [Model Context Protocol](https://modelcontextprotocol.io/) for secure, standardized data access:

| Provider | MCP Server | Skills Using |
|----------|------------|--------------|
| [GitHub](https://github.com/) | `mcp-github` | presearch, url-fetcher |
| [Brave Search](https://search.brave.com/) | `mcp-brave-search` | presearch, url-fetcher |
| arXiv | `mcp-arxiv` | presearch |
| Playwright | `mcp-playwright` | url-fetcher |
| Fetch | `mcp-fetch` | url-fetcher |
| Yahoo Finance | `yahoo-finance` | earnings-analyzer, macro-brief |
| Alpha Vantage | `alpha-vantage` | earnings-analyzer |
| FRED | `fred-api` | macro-brief |

### Installation

#### Prerequisites

| Requirement | Installation |
|-------------|--------------|
| **bash** | Built-in (macOS/Linux), Git Bash (Windows) |
| **curl** | Built-in (macOS/Linux), Git Bash (Windows) |
| **python3** | [python.org](https://python.org) or `brew install python` |
| **uv** (recommended) | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |

#### Quick Install

```bash
# Clone and install
git clone https://github.com/quinnmacro/quinn-awesome-skills.git
cd quinn-awesome-skills
bash install.sh
```

#### Install Specific Skill

```bash
bash install.sh presearch     # Install only presearch
bash install.sh url-fetcher   # Install only url-fetcher
```

#### What Gets Installed

| Target | Purpose |
|--------|---------|
| `~/.agent/skills/` | Skill files (canonical location) |
| `~/.claude/skills/` | Symlink for Claude Code |
| `~/.openclaw/skills/` | Symlink for OpenClaw |
| `~/.claude/commands/` | Slash command definitions |
| `~/.claude/connectors/` | MCP configuration |

### Usage

#### Slash Commands

```bash
# Core
/url-fetcher https://example.com
/url-fetcher "search query"           # Web search
/presearch "React framework"
/presearch "Python async" emoji       # Fun format

# Investment
/investor-distiller 巴菲特
/investor-distiller Dalio
/macro-brief daily
/macro-brief weekly
/earnings-analyzer AAPL
/earnings-analyzer 苹果 2024Q4

# Creative
/creative-prompt "sci-fi story"
/dev-joke python
/dev-joke "debugging"
/code-poet "quick sort"
/code-poet --style haiku "recursion"
```

#### Skill Auto-Trigger

Skills automatically activate based on context:

| Trigger Pattern | Skill Activated |
|-----------------|-----------------|
| URL in message | url-fetcher |
| "找库", "找轮子", "有没有现成的" | presearch |
| "财报分析", "财务报表" | earnings-analyzer |
| "投资大师", "巴菲特" | investor-distiller |
| "宏观经济", "市场分析" | macro-brief |

### Dependencies

| Feature | Dependencies | Install Command |
|---------|--------------|-----------------|
| **Core** | bash, curl, python3 | System package manager |
| **WeChat** | playwright, beautifulsoup4, lxml | `uv pip install playwright beautifulsoup4 lxml && playwright install chromium` |
| **Feishu** | `FEISHU_APP_ID` + `FEISHU_APP_SECRET` | Set environment variables |
| **PDF** | marker-pdf or poppler | `uv pip install marker-pdf` or `brew install poppler` |
| **Web Search** | open-websearch | `npx open-websearch@latest` |
| **arXiv** | arxiv | `uv pip install arxiv` |
| **LLM Agent** | requests | `uv pip install requests` |

### Configuration

Copy `.env.example` to `.env` and configure:

```bash
# LLM Provider (default: infini)
LLM_PROVIDER=infini
INFINI_API_KEY=your_key

# Or use Anthropic
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_key

# Feishu Integration
FEISHU_APP_ID=your_app_id
FEISHU_APP_SECRET=your_app_secret

# Financial Data (optional)
ALPHA_VANTAGE_API_KEY=your_key
FRED_API_KEY=your_key
```

---

## 中文

### 技能概览

#### 核心技能

| 技能 | 描述 | 命令 | 状态 |
|------|------|------|------|
| [url-fetcher](skills/core/url-fetcher/) | 将任意 URL 转为 Markdown。微信公众号、飞书、PDF、网页搜索。 | `/url-fetcher` | ✅ 生产可用 |
| [presearch](skills/core/presearch/) | 开发前搜索现有方案。GitHub、npm、PyPI、Docker Hub、arXiv。 | `/presearch` | ✅ 生产可用 |

#### 投资技能

| 技能 | 描述 | 命令 | 状态 |
|------|------|------|------|
| [investor-distiller](skills/investment/investor-distiller/) | 蒸馏投资大师的投资哲学和方法论。 | `/investor-distiller` | ✅ 生产可用 |
| [macro-brief](skills/investment/macro-brief/) | 生成宏观经济简报和市场分析。 | `/macro-brief` | ✅ 生产可用 |
| [earnings-analyzer](skills/investment/earnings-analyzer/) | 分析上市公司财务报表。 | `/earnings-analyzer` | ✅ 生产可用 |

#### 创意技能

| 技能 | 描述 | 命令 | 状态 |
|------|------|------|------|
| [creative-prompt](skills/creative/creative-prompt/) | 生成创意提示，用于写作和设计。 | `/creative-prompt` | ✅ 生产可用 |
| [dev-joke](skills/creative/dev-joke/) | 开发者笑话和编程幽默。 | `/dev-joke` | ✅ 生产可用 |
| [code-poet](skills/creative/code-poet/) | 将代码转化为诗歌。 | `/code-poet` | ✅ 生产可用 |

### 详细功能

#### URL Fetcher — 通用内容提取

支持多种平台，零配置即可使用：

| 平台 | 方法 | 功能 |
|------|------|------|
| **微信公众号** | Playwright 抓取 | 完整文章，保留格式 |
| **飞书/Lark** | 官方 API | 文档、Wiki、表格 |
| **X/Twitter** | fxtwitter.com | 推文、线程、媒体 |
| **Instagram** | fxstagram.com | 帖子、Reels、图片 |
| **TikTok** | tnktok.com | 视频、图片 |
| **Reddit** | vxreddit.com | 帖子、评论 |
| **PDF** | marker-pdf / pdftotext | 远程 URL 和本地文件 |
| **网页搜索** | open-websearch | 8 个搜索引擎，无需 API key |

#### Presearch — 开发者资源智能搜索

造轮子前，先搜索现有方案：

| 来源 | 数据 | 健康检查 |
|------|------|----------|
| **GitHub** | Stars、Forks、Issues、最后提交 | 活跃度评分、维护状态 |
| **npm** | 下载量、依赖、版本 | 安全审计、弃用状态 |
| **PyPI** | 下载量、依赖、版本 | 安全审计 |
| **Docker Hub** | 拉取量、Stars、最后更新 | 官方状态 |
| **arXiv** | 论文、引用、作者 | 相关论文 |

**输出格式**: `default` | `emoji` | `meme` | `poetry`

### MCP 数据连接器

所有连接器使用 [Model Context Protocol](https://modelcontextprotocol.io/) 实现安全、标准化的数据访问：

| 提供商 | MCP 服务器 | 使用技能 |
|--------|-----------|----------|
| GitHub | `mcp-github` | presearch, url-fetcher |
| Brave Search | `mcp-brave-search` | presearch, url-fetcher |
| arXiv | `mcp-arxiv` | presearch |
| Playwright | `mcp-playwright` | url-fetcher |
| Yahoo Finance | `yahoo-finance` | earnings-analyzer, macro-brief |

### 安装

```bash
# 克隆并安装
git clone https://github.com/quinnmacro/quinn-awesome-skills.git
cd quinn-awesome-skills
bash install.sh

# 安装特定技能
bash install.sh presearch
```

### 使用示例

```bash
# 核心
/url-fetcher https://mp.weixin.qq.com/s/xxx
/presearch "Python web framework" emoji

# 投资
/investor-distiller 巴菲特
/macro-brief weekly
/earnings-analyzer 苹果

# 创意
/dev-joke python
/code-poet "递归"
```

### 环境配置

复制 `.env.example` 到 `.env` 并配置：

| 配置项 | 用途 |
|--------|------|
| `FEISHU_APP_ID` + `FEISHU_APP_SECRET` | 飞书文档抓取 |
| `INFINI_API_KEY` | LLM Agent |
| `ALPHA_VANTAGE_API_KEY` | 金融数据 |
| `FRED_API_KEY` | 宏观经济数据 |

---

## Comparison with Finance Context

| Feature | Finance Context | quinn-awesome-skills |
|---------|-----------------|---------------------|
| **Architecture** | Skills/Commands/Connectors | ✅ Same + domain-based organization |
| **Domains** | Finance only | Finance + Core utilities + Creative |
| **Social Media** | Not supported | ✅ 8 platforms via fixer services |
| **Chinese Platforms** | Not supported | ✅ WeChat, Feishu via API |
| **Web Search** | Via MCP only | ✅ Built-in, 8 engines, no API key |
| **arXiv** | Not supported | ✅ Academic paper search |
| **Output Formats** | Standard | ✅ emoji, meme, poetry options |
| **Installation** | Manual config | ✅ Single `bash install.sh` |
| **Windows Support** | Limited | ✅ Full Windows support |
| **Open Source** | Partial | ✅ Fully open source |

---

## Roadmap

### v1.1 (Planned)

- [ ] Add `/dcf` DCF valuation command
- [ ] Add `/comps` comparable company analysis
- [ ] Add `/lbo` LBO model command
- [ ] Integrate Bloomberg MCP connector
- [ ] Add Chinese A-share data support

### v1.2 (Planned)

- [ ] Skill marketplace for community contributions
- [ ] Auto-update mechanism
- [ ] Performance benchmarks and metrics
- [ ] VS Code extension integration

---

## Project Structure

```
quinn-awesome-skills/
├── skills/                    # 按领域划分的技能
│   ├── core/                  # 核心技能
│   │   ├── url-fetcher/       # URL 抓取
│   │   └── presearch/         # 开发前搜索
│   ├── investment/            # 投资技能
│   │   ├── investor-distiller/
│   │   ├── macro-brief/
│   │   └── earnings-analyzer/
│   └── creative/              # 创意技能
│       ├── creative-prompt/
│       ├── dev-joke/
│       └── code-poet/
├── commands/                  # 斜杠命令（独立文件）
│   ├── url-fetcher.md
│   ├── presearch.md
│   └── ...
├── connectors/                # MCP 连接器配置
│   └── mcp-servers.json
├── scripts/                   # 公共脚本
│   ├── llm_agent.py          # LLM Agent
│   └── llm.sh                # LLM 包装脚本
├── templates/                 # 模板文件
├── .claude/commands/         # 自定义命令
├── README.md                  # 项目文档（双语）
├── AGENTS.md                  # AI Agent 上下文
├── CLAUDE.md                  # Claude Code 配置
└── install.sh                 # 安装脚本
```

---

## Resources

- [Claude Code Skills Documentation](https://docs.claude.com/en/docs/claude-code/skills)
- [anthropics/skills](https://github.com/anthropics/skills) - Anthropic 官方 skills
- [Finance Context](https://github.com/LLMQuant/docs) - 金融版 Claude Skills
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP 官方文档

## Contributing

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

**贡献指南：**
1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-skill`)
3. 提交更改 (`git commit -m 'Add amazing skill'`)
4. 推送到分支 (`git push origin feature/amazing-skill`)
5. 创建 Pull Request

**Skill 贡献格式：**
```
skills/
└── your-domain/
    └── your-skill/
        ├── SKILL.md          # Required: Skill definition
        ├── scripts/          # Optional: Helper scripts
        └── references/       # Optional: Documentation
```

## License

MIT License - 详见 [LICENSE](LICENSE)。

---

**Author**: [@quinnmacro](https://github.com/quinnmacro)

**Star this repo** if you find it helpful! / 觉得有用请点个 **Star**！

[⬆ Back to Top](#quinn-awesome-skills)
