# quinn-awesome-skills

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
![Skills Count](https://img.shields.io/badge/skills-8-brightgreen)

> Personal collection of Claude Code skills for AI-native development workflows
> 
> 个人维护的 Claude Code skills 集合，采用 Skills/Commands/Connectors 三层架构

[English](#english) | [中文](#中文)

---

## Architecture 架构

```
quinn-awesome-skills/
├── skills/                    # 技能（按领域划分）
│   ├── core/                  # 核心技能
│   ├── investment/            # 投资技能
│   └── creative/              # 创意技能
├── commands/                  # 斜杠命令
├── connectors/                # MCP 连接器配置
└── scripts/                   # 共享脚本
```

**三层架构说明：**
- **Skills**: 领域专业知识编码，自动触发
- **Commands**: 斜杠命令，显式调用
- **Connectors**: MCP 数据连接器

---

## English

### Skills

#### Core 核心技能

| Skill | Description | Command |
|-------|-------------|---------|
| [url-fetcher](skills/core/url-fetcher/) | Fetch any URL as clean Markdown. WeChat, Feishu, PDF, Web search. | `/url-fetcher` |
| [presearch](skills/core/presearch/) | Search developer resources. GitHub, npm, PyPI, Docker Hub, arXiv. | `/presearch` |

#### Investment 投资技能

| Skill | Description | Command |
|-------|-------------|---------|
| [investor-distiller](skills/investment/investor-distiller/) | Extract investment wisdom from legendary investors. | `/investor-distiller` |
| [macro-brief](skills/investment/macro-brief/) | Generate macroeconomic briefs and market analysis. | `/macro-brief` |
| [earnings-analyzer](skills/investment/earnings-analyzer/) | Analyze financial statements and earnings reports. | `/earnings-analyzer` |

#### Creative 创意技能

| Skill | Description | Command |
|-------|-------------|---------|
| [creative-prompt](skills/creative/creative-prompt/) | Generate creative prompts for writing and design. | `/creative-prompt` |
| [dev-joke](skills/creative/dev-joke/) | Developer jokes and coding humor. | `/dev-joke` |
| [code-poet](skills/creative/code-poet/) | Transform code into poetry. | `/code-poet` |

### Features

**URL Fetcher** - Convert any URL to clean Markdown:
- 🔗 **Social Media**: X/Twitter, Instagram, TikTok, Reddit, Threads, Bluesky
- 📱 **Chinese Platforms**: WeChat 公众号, Feishu/Lark docs
- 📄 **Documents**: PDF extraction (remote & local)
- 🔍 **Web Search**: 8 engines, no API key required

**Presearch** - Search developer resources before building:
- 🐙 **GitHub**: Open source projects sorted by stars
- 📦 **npm/PyPI**: JavaScript and Python packages
- 📚 **arXiv**: Academic papers
- 🏥 **Health Assessment**: Project activity, stars, maintenance status
- 🎨 **Fun Formats**: emoji, meme, poetry output styles

**Investment Skills** - Professional investment analysis:
- 📊 **Investor Distiller**: Extract frameworks from Buffett, Munger, Dalio
- 📈 **Macro Brief**: Economic analysis and market summaries
- 💰 **Earnings Analyzer**: Financial statement analysis

### Installation

```bash
# Quick install
git clone https://github.com/quinnmacro/quinn-awesome-skills.git
cd quinn-awesome-skills
bash install.sh

# Install specific skill
bash install.sh presearch
```

This will:
- Install skills to `~/.agent/skills/`
- Create symlinks to `~/.claude/skills/`
- Install commands to `~/.claude/commands/`
- Copy connector configs to `~/.claude/connectors/`

### Usage

```bash
# Use slash commands
/url-fetcher https://example.com
/presearch "React framework" emoji
/investor-distiller 巴菲特
/macro-brief weekly
/earnings-analyzer 苹果
```

### Requirements

| Feature | Dependencies |
|---------|--------------|
| Core | bash, curl, python3 |
| WeChat | `pip install playwright beautifulsoup4 lxml` |
| Feishu | Set `FEISHU_APP_ID` + `FEISHU_APP_SECRET` |
| PDF | `pip install marker-pdf` or `brew install poppler` |
| Search | `npx open-websearch@latest` |
| arXiv | `pip install arxiv` |

---

## 中文

### 技能列表

#### Core 核心技能

| Skill | 描述 | 命令 |
|-------|------|------|
| [url-fetcher](skills/core/url-fetcher/) | 将任意 URL 转为 Markdown。微信公众号、飞书、PDF、网页搜索。 | `/url-fetcher` |
| [presearch](skills/core/presearch/) | 开发前搜索现有方案。GitHub、npm、PyPI、Docker Hub、arXiv。 | `/presearch` |

#### Investment 投资技能

| Skill | 描述 | 命令 |
|-------|------|------|
| [investor-distiller](skills/investment/investor-distiller/) | 蒸馏投资大师的投资哲学和方法论。 | `/investor-distiller` |
| [macro-brief](skills/investment/macro-brief/) | 生成宏观经济简报和市场分析。 | `/macro-brief` |
| [earnings-analyzer](skills/investment/earnings-analyzer/) | 分析上市公司财务报表。 | `/earnings-analyzer` |

#### Creative 创意技能

| Skill | 描述 | 命令 |
|-------|------|------|
| [creative-prompt](skills/creative/creative-prompt/) | 生成创意提示，用于写作和设计。 | `/creative-prompt` |
| [dev-joke](skills/creative/dev-joke/) | 开发者笑话和编程幽默。 | `/dev-joke` |
| [code-poet](skills/creative/code-poet/) | 将代码转化为诗歌。 | `/code-poet` |

### 安装

```bash
# 快速安装
git clone https://github.com/quinnmacro/quinn-awesome-skills.git
cd quinn-awesome-skills
bash install.sh
```

### 使用示例

```bash
# 斜杠命令
/url-fetcher https://mp.weixin.qq.com/s/xxx
/presearch "Python web framework" emoji
/investor-distiller 巴菲特
```

### 环境配置

复制 `.env.example` 到 `.env` 并配置：

| 配置项 | 用途 |
|--------|------|
| `FEISHU_APP_ID` + `FEISHU_APP_SECRET` | 飞书文档抓取 |
| `INFINI_API_KEY` | LLM Agent |

---

## Project Structure 项目结构

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
├── connectors/                # MCP 连接器配置
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

## Resources 资源

- [Claude Code Skills Documentation](https://docs.claude.com/en/docs/claude-code/skills)
- [anthropics/skills](https://github.com/anthropics/skills) - Anthropic 官方 skills
- [Finance Context](https://github.com/LLMQuant/docs) - 金融版 Claude Skills

## Contributing 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

## License 许可证

MIT License - 详见 [LICENSE](LICENSE)。

---

**Author 作者**: [@quinnmacro](https://github.com/quinnmacro)

**Star this repo** if you find it helpful! ⭐ / 觉得有用请点个 **Star**！⭐
