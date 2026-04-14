---
name: presearch
description: |
  开发前搜索现有方案，避免重复造轮子。
  搜索 GitHub, npm, PyPI, Docker Hub, arXiv 等开发者资源。
  支持项目健康度评估、多种输出格式。
  Triggers: "找库", "找轮子", "有没有现成的", "presearch".
version: 3.0.0
author: quinnmacro
---

# Presearch - 开发前搜索

开发前搜索现有方案，避免重复造轮子。

## 用法

```bash
# 基本搜索
bash ~/.claude/skills/presearch/scripts/presearch.sh "Python web framework"

# 指定输出格式
bash ~/.claude/skills/presearch/scripts/presearch.sh "React" emoji
```

## 输出格式

| 格式 | 说明 |
|------|------|
| `table` | 默认表格格式 |
| `json` | JSON 格式 |
| `csv` | CSV 格式 |
| `markdown` | Markdown 表格 |
| `emoji` | 表情符号装饰 |
| `meme` | 程序员梗图风格 |
| `poetry` | 诗歌形式 |
| `fortune` | 幸运饼干风格 |

## 数据源

| 数据源 | 说明 |
|--------|------|
| GitHub | 开源项目，按 stars 排序 |
| npm | JavaScript 包 |
| PyPI | Python 包 |
| Docker Hub | 容器镜像 |
| arXiv | 学术论文 |

## 项目健康度

- 🟢 优秀：>1000 stars/downloads，6个月内更新
- 🟡 良好：>100 stars/downloads，6个月内更新
- 🟠 一般：>10 stars/downloads
- 🔴 新项目：其他情况

## 依赖

```bash
pip install requests pydantic pydantic-settings
```

**注意**: Ubuntu 24.04+ 需要先安装 venv：
```bash
apt install python3.12-venv
cd ~/.claude/skills/presearch
python3 -m venv venv && source venv/bin/activate
pip install requests pydantic pydantic-settings
```

## CLI 高级用法

```bash
# 直接使用 Python 模块
python3 ~/.claude/skills/presearch/modules/presearch_core.py "query" -f json

# 查看缓存统计
python3 ~/.claude/skills/presearch/modules/presearch_core.py --cache-stats

# 清除缓存
python3 ~/.claude/skills/presearch/modules/presearch_core.py --clear-cache

# 查看历史
python3 ~/.claude/skills/presearch/modules/presearch_core.py -H
```

## 注意

- GitHub API 有速率限制
- 缓存默认 24 小时过期
- 支持中英文混合搜索
