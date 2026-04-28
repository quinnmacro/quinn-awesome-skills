---
description: 开发者早报 — GitHub活动、安全警报、包更新、新闻聚合、待办事项
allowed-tools: Bash(gh *), Bash(curl *), Bash(bash *), Bash(python3 *), Bash(mkdir *), Bash(cat *)
---

# /daily-dev-pulse - 开发者早报

生成个性化开发者早报，涵盖 GitHub 活动、安全警报、包更新、技术新闻和待办事项。

## 用法

```
/daily-dev-pulse                  # 完整早报 (默认)
/daily-dev-pulse --focus security # 只看安全警报
/daily-dev-pulse --focus news     # 只看技术新闻
/daily-dev-pulse --format md      # Markdown 输出
/daily-dev-pulse --format json    # JSON 输出
/daily-dev-pulse --repos quinnmacro/quinn-awesome-skills  # 指定仓库
/daily-dev-pulse --days 30        # 30天活动回顾
```

## 工作流

1. **加载配置** — 读取 `~/.quinn-skills/pulse-config.yml`，无配置则使用默认值
2. **收集数据** — 运行 `bash ~/.claude/skills/daily-dev-pulse/scripts/daily-dev-pulse.sh --format md`
3. **展示结果** — 将格式化后的早报展示给用户

## 数据源

| 源 | 方法 | 内容 |
|----|------|------|
| GitHub | `gh` CLI | commits, PRs, issues, CI status |
| NVD | API | CVE 安全警报 |
| Hacker News | API | Top 10 文章 |
| Dev.to | API | 热门文章 |
| npm/PyPI | Registry API | 包更新 |

## 依赖

- gh CLI (`brew install gh`)
- python3 + pyyaml (`pip install pyyaml`)

## 相关技能

- url-fetcher — 新闻文章内容提取
- presearch — 包趋势搜索