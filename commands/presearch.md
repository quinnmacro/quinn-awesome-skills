---
description: 开发前搜索现有方案，避免重复造轮子。用法：/presearch <功能描述> [格式]
allowed-tools: Bash(curl *), Bash(python3 *)
---

# /presearch - 开发前搜索

开发前搜索现有方案，避免重复造轮子。

## 用法

```
/presearch <功能描述>
/presearch "React framework" emoji      # 表情包格式
/presearch "Python web" json            # JSON 格式
```

## 工作流

1. **提取关键词** - 分析查询意图
2. **并行搜索** - GitHub, npm, PyPI, Docker Hub, arXiv
3. **健康度评估** - 项目活跃度、stars、维护状态
4. **格式输出** - table/emoji/meme/poetry/json

## 数据源

| 数据源 | 说明 |
|--------|------|
| GitHub | 开源项目，按 stars 排序 |
| npm | JavaScript 包 |
| PyPI | Python 包 |
| Docker Hub | 容器镜像 |
| arXiv | 学术论文 |

## 输出格式

| 格式 | 说明 |
|------|------|
| `table` | 默认表格格式 |
| `emoji` | 表情符号装饰 |
| `meme` | 程序员梗图风格 |
| `poetry` | 诗歌形式 |
| `json` | JSON 格式 |

## 依赖

```bash
pip install requests pydantic arxiv
```

## 相关技能

- url-fetcher - 获取搜索结果的详细内容
