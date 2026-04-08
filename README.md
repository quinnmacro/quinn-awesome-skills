# quinn-awesome-skills

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
![Skills Count](https://img.shields.io/badge/skills-8-brightgreen)

> Personal collection of Claude Code skills for AI-native development workflows
> 
> 个人维护的 Claude Code skills 集合，聚焦于 URL 处理、内容抓取、Web 搜索等实用功能

[English](#english) | [中文](#中文)

---

## English

### Skills

| Skill | Description | Category |
|-------|-------------|----------|
| [url-fetcher](skills/url-fetcher/) | Fetch any URL as clean Markdown. Supports X/Twitter, WeChat, Feishu, PDFs, and web search. | 📄 Content |
| [presearch](skills/presearch/) | Search developer resources before building. GitHub, npm, PyPI, Docker Hub, arXiv with health assessment. | 🔍 Research |
| [investor-distiller](skills/investor-distiller/) | Extract investment wisdom from legendary investors into actionable frameworks. Buffett, Munger, Dalio, etc. | 📊 Investment |
| [macro-brief](skills/macro-brief/) | Generate macroeconomic briefs, market summaries, and economic analysis reports. | 📈 Macro |
| [earnings-analyzer](skills/earnings-analyzer/) | Analyze financial statements and earnings reports with key metrics and insights. | 💰 Finance |
| [creative-prompt](skills/creative-prompt/) | Generate creative prompts for writing, design, brainstorming, and ideation. | 💡 Creativity |
| [dev-joke](skills/dev-joke/) | Developer jokes, coding humor, and tech memes. Perfect for debugging morale boost. | 😄 Humor |
| [code-poet](skills/code-poet/) | Transform code into poetry, write code-inspired poems, or explain code poetically. | 📜 Art |

### Features

**URL Fetcher** - Convert any URL to clean Markdown:
- 🔗 **Social Media**: X/Twitter, Instagram, TikTok, Reddit, Threads, Bluesky (no login required)
- 📱 **Chinese Platforms**: WeChat 公众号, Feishu/Lark docs
- 📄 **Documents**: PDF extraction (remote & local)
- 🔍 **Web Search**: 8 engines, no API key required
- 🤖 **LLM Agent**: Built-in LLM integration for summarization, translation, analysis

**Presearch** - Search developer resources before building:
- 🐙 **GitHub**: Open source projects sorted by stars
- 📦 **npm/PyPI**: JavaScript and Python packages
- 🐳 **Docker Hub**: Container images with pull counts
- 📚 **arXiv**: Academic papers
- 🏥 **Health Assessment**: Project activity, stars, maintenance status
- 🎨 **Fun Formats**: emoji, meme, poetry output styles

**Investment Skills** - Professional investment analysis:
- 📊 **Investor Distiller**: Extract frameworks from Buffett, Munger, Dalio
- 📈 **Macro Brief**: Economic analysis and market summaries
- 💰 **Earnings Analyzer**: Financial statement analysis

### Installation

```bash
# Quick install (recommended)
git clone https://github.com/quinnmacro/quinn-awesome-skills.git
cd quinn-awesome-skills
bash install.sh

# Or one-liner
curl -sL https://raw.githubusercontent.com/quinnmacro/quinn-awesome-skills/main/install.sh | bash
```

This will:
- Install skills to `~/.agent/skills/`
- Create symlinks to `~/.claude/skills/` and `~/.openclaw/skills/`
- Set up slash commands (`/url-fetcher`, `/presearch`)

### Usage

```bash
# Use slash commands in Claude Code
/url-fetcher https://example.com
/presearch "React framework"

# Or call scripts directly
bash ~/.claude/skills/url-fetcher/scripts/fetch.sh "https://example.com"
bash ~/.claude/skills/url-fetcher/scripts/search.sh "query" duckduckgo 5

# Presearch with fun format
python3 ~/.claude/skills/presearch/modules/presearch_core.py "Python web framework" -f emoji
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
| [url-fetcher](skills/url-fetcher/) | 将任意 URL 转为干净的 Markdown。支持 X/Twitter、微信公众号、飞书文档、PDF 和网页搜索。 | 📄 内容 |
| [presearch](skills/presearch/) | 开发前搜索现有方案。GitHub、npm、PyPI、Docker Hub、arXiv，带项目健康度评估。 | 🔍 调研 |
| [investor-distiller](skills/investor-distiller/) | 蒸馏投资大师的投资哲学和方法论，生成可执行的分析框架。巴菲特、芒格、达利欧等。 | 📊 投资 |
| [macro-brief](skills/macro-brief/) | 生成宏观经济简报、市场分析和经济数据解读。 | 📈 宏观 |
| [earnings-analyzer](skills/earnings-analyzer/) | 分析上市公司财务报表，提取关键指标和投资洞察。 | 💰 财报 |
| [creative-prompt](skills/creative-prompt/) | 生成创意提示，用于写作、设计、头脑风暴和创意构思。 | 💡 创意 |
| [dev-joke](skills/dev-joke/) | 开发者笑话、编程幽默和技术梗图。调试时提振士气必备。 | 😄 幽默 |
| [code-poet](skills/code-poet/) | 将代码转化为诗歌，编写代码主题诗，或用诗意语言解释代码。 | 📜 艺术 |

### 功能特性

**URL Fetcher** - 将任意 URL 转换为干净的 Markdown：
- 🔗 **社交媒体**: X/Twitter、Instagram、TikTok、Reddit、Threads、Bluesky（无需登录）
- 📱 **中文平台**: 微信公众号、飞书/Lark 文档
- 📄 **文档处理**: PDF 提取（支持远程和本地）
- 🔍 **网页搜索**: 8 个搜索引擎，无需 API key
- 🤖 **LLM 集成**: 内置 LLM Agent，支持摘要、翻译、分析

**Presearch** - 开发前搜索现有方案：
- 🐙 **GitHub**: 开源项目，按 stars 排序
- 📦 **npm/PyPI**: JavaScript 和 Python 包
- 🐳 **Docker Hub**: 容器镜像及下载量
- 📚 **arXiv**: 学术论文
- 🏥 **健康度评估**: 项目活跃度、stars、维护状态
- 🎨 **趣味格式**: emoji、meme、诗歌等输出风格

**投资技能** - 专业投资分析：
- 📊 **投资大师蒸馏**: 提炼巴菲特、芒格、达利欧的投资框架
- 📈 **宏观简报**: 经济分析和市场总结
- 💰 **财报分析**: 财务报表分析

### 安装

```bash
# 快速安装（推荐）
git clone https://github.com/quinnmacro/quinn-awesome-skills.git
cd quinn-awesome-skills
bash install.sh

# 或一键安装
curl -sL https://raw.githubusercontent.com/quinnmacro/quinn-awesome-skills/main/install.sh | bash
```

安装后会：
- 将 skills 安装到 `~/.agent/skills/`
- 创建软链接到 `~/.claude/skills/` 和 `~/.openclaw/skills/`
- 设置斜杠命令（`/url-fetcher`、`/presearch`）

### 使用示例

```bash
# 在 Claude Code 中使用斜杠命令
/url-fetcher https://example.com
/presearch "React 框架"

# 或直接调用脚本
bash ~/.claude/skills/url-fetcher/scripts/fetch.sh "https://example.com"
bash ~/.claude/skills/url-fetcher/scripts/search.sh "关键词" duckduckgo 5

# Presearch 使用趣味格式
python3 ~/.claude/skills/presearch/modules/presearch_core.py "Python web framework" -f emoji
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
├── install.sh             # 一键安装脚本
├── skills/                # 技能目录
│   ├── url-fetcher/       # URL 抓取
│   ├── presearch/         # 开发前搜索
│   ├── investor-distiller/ # 投资大师蒸馏
│   ├── macro-brief/       # 宏观简报
│   ├── earnings-analyzer/ # 财报分析
│   ├── creative-prompt/   # 创意提示
│   ├── dev-joke/          # 开发者笑话
│   └── code-poet/         # 代码诗人
├── scripts/               # 公共脚本
│   ├── llm_agent.py       # LLM Agent
│   └── llm.sh             # LLM 包装脚本
├── templates/             # 模板文件
│   └── SKILL_TEMPLATE.md  # Skill 模板
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
