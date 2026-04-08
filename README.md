# quinn-awesome-skills

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
![Skills Count](https://img.shields.io/badge/skills-1-brightgreen)

> Personal collection of Claude Code skills for AI-native development workflows
> 
> 个人维护的 Claude Code skills 集合，聚焦于 URL 处理、内容抓取、Web 搜索等实用功能

[English](#english) | [中文](#中文)

---

## English

### Skills

| Skill | Description | Category |
|-------|-------------|----------|
| [url-fetcher](skills/url-fetcher/) | Fetch any URL as clean Markdown. Supports X/Twitter, WeChat, Feishu, PDFs, and web search. | 📄 Content Fetching |

### Features

**URL Fetcher** - Convert any URL to clean Markdown:
- 🔗 **Social Media**: X/Twitter, Instagram, TikTok, Reddit, Threads, Bluesky (no login required)
- 📱 **Chinese Platforms**: WeChat 公众号, Feishu/Lark docs
- 📄 **Documents**: PDF extraction (remote & local)
- 🔍 **Web Search**: 8 engines, no API key required
- 🤖 **LLM Agent**: Built-in LLM integration for summarization, translation, analysis

### Installation

```bash
# Quick install
git clone https://github.com/quinnmacro/quinn-awesome-skills.git ~/.claude/skills/quinn-awesome-skills

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Usage

```bash
# Fetch URL as Markdown
bash skills/url-fetcher/scripts/fetch.sh "https://example.com"

# Web search (no API key)
bash skills/url-fetcher/scripts/search.sh "query" duckduckgo 5

# LLM agent
bash scripts/llm.sh "Summarize this text" --json
```

### Requirements

| Feature | Dependencies |
|---------|--------------|
| Core | bash, curl, python3 |
| WeChat | `pip install playwright beautifulsoup4 lxml` |
| Feishu | Set `FEISHU_APP_ID` + `FEISHU_APP_SECRET` |
| PDF | `pip install marker-pdf` or `brew install poppler` |
| Search | `npx open-websearch@latest` |
| LLM | `pip install requests` + API key in `.env` |

### Supported Platforms

| Platform | Method | Auth |
|----------|--------|------|
| X/Twitter | fxtwitter.com | ❌ |
| Instagram | fxstagram.com | ❌ |
| TikTok | tnktok.com | ❌ |
| Reddit | vxreddit.com | ❌ |
| Threads | fixthreads.seria.moe | ❌ |
| Bluesky | fxbsky.app | ❌ |
| WeChat 公众号 | Playwright | ❌ |
| Feishu/Lark | API | ✅ |
| PDF | marker-pdf/pdftotext | ❌ |

---

## 中文

### 技能列表

| Skill | 描述 | 分类 |
|-------|------|------|
| [url-fetcher](skills/url-fetcher/) | 将任意 URL 转为干净的 Markdown。支持 X/Twitter、微信公众号、飞书文档、PDF 和网页搜索。 | 📄 内容抓取 |

### 功能特性

**URL Fetcher** - 将任意 URL 转换为干净的 Markdown：
- 🔗 **社交媒体**: X/Twitter、Instagram、TikTok、Reddit、Threads、Bluesky（无需登录）
- 📱 **中文平台**: 微信公众号、飞书/Lark 文档
- 📄 **文档处理**: PDF 提取（支持远程和本地）
- 🔍 **网页搜索**: 8 个搜索引擎，无需 API key
- 🤖 **LLM 集成**: 内置 LLM Agent，支持摘要、翻译、分析

### 安装

```bash
# 快速安装
git clone https://github.com/quinnmacro/quinn-awesome-skills.git ~/.claude/skills/quinn-awesome-skills

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入你的 API keys
```

### 使用示例

```bash
# 获取网页内容
bash skills/url-fetcher/scripts/fetch.sh "https://example.com"

# 网页搜索（无需 API key）
bash skills/url-fetcher/scripts/search.sh "关键词" duckduckgo 5

# LLM 调用
bash scripts/llm.sh "总结这段文字" --json
```

### 环境配置

复制 `.env.example` 到 `.env` 并配置：

| 配置项 | 用途 | 必需 |
|--------|------|------|
| `FEISHU_APP_ID` + `FEISHU_APP_SECRET` | 飞书文档抓取 | ✅ 飞书功能 |
| `INFINI_API_KEY` | Infini GenStudio LLM | ✅ LLM Agent |
| `ANTHROPIC_API_KEY` | Anthropic Claude LLM | ✅ LLM Agent (备选) |
| `USE_PROXY` + `PROXY_URL` | 代理配置 | ❌ 可选 |
| `JINA_API_KEY` | Jina 搜索 API | ❌ 可选 |

### 依赖要求

| 功能 | 依赖 |
|------|------|
| 核心 | bash, curl, python3 |
| 微信公众号 | `pip install playwright beautifulsoup4 lxml && playwright install chromium` |
| 飞书 | 设置环境变量 `FEISHU_APP_ID` + `FEISHU_APP_SECRET` |
| PDF | `pip install marker-pdf`（推荐）或 `brew install poppler` |
| 搜索 | `npx open-websearch@latest` |
| LLM | `pip install requests` + `.env` 配置 |

### 项目结构

```
quinn-awesome-skills/
├── README.md              # 项目文档（双语）
├── AGENTS.md              # AI Agent 上下文
├── CLAUDE.md              # Claude Code 配置
├── CHANGELOG.md           # 版本历史
├── CONTRIBUTING.md        # 贡献指南
├── .env.example           # 环境变量模板
├── skills/                # 技能目录
│   └── url-fetcher/
│       ├── SKILL.md       # 技能定义
│       ├── scripts/       # 脚本文件
│       └── references/    # 参考文档
├── scripts/               # 公共脚本
│   ├── llm_agent.py       # LLM Agent
│   └── llm.sh             # LLM 包装脚本
├── memory/                # 项目记忆
└── .claude/commands/      # 自定义命令
```

---

## Resources 资源

- [Claude Code Skills Documentation](https://docs.claude.com/en/docs/claude-code/skills) - 官方文档
- [anthropics/skills](https://github.com/anthropics/skills) - Anthropic 官方 skills
- [obra/superpowers](https://github.com/obra/superpowers) - 实战技能库
- [awesome-claude-skills](https://github.com/karanb192/awesome-claude-skills) - 社区合集

## Contributing 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

## License 许可证

MIT License - 详见 [LICENSE](LICENSE)。

---

**Author 作者**: [@quinnmacro](https://github.com/quinnmacro)

**Star this repo** if you find it helpful! ⭐ / 觉得有用请点个 **Star**！⭐
