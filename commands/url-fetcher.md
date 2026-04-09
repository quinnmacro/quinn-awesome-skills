---
description: 获取任意 URL 内容转为 Markdown，支持公众号、飞书、社交媒体、PDF、Web搜索
allowed-tools: Bash(curl *), Bash(bash *), Bash(python3 *)
---

# /url-fetcher - URL 转 Markdown

将任意 URL 转为干净的 Markdown。支持需要登录的页面、PDF、专有平台。

## 用法

```
/url-fetcher <URL>
/url-fetcher <search query>    # Web 搜索
```

## 工作流

1. **判断 URL 类型** - 根据域名选择处理脚本
2. **获取内容** - 执行对应脚本
3. **显示结果** - 标题、来源、摘要、正文
4. **保存文件** - 默认保存到 `~/Downloads/{title}.md`

## URL 路由

| URL 类型 | 处理方式 |
|----------|----------|
| 微信公众号 | `python3 scripts/fetch_weixin.py "URL"` |
| 飞书文档 | `python3 scripts/fetch_feishu.py "URL"` |
| Twitter/X | `bash scripts/fetch.sh "URL"` |
| Instagram | `bash scripts/fetch.sh "URL"` |
| TikTok | `bash scripts/fetch.sh "URL"` |
| Reddit | `bash scripts/fetch.sh "URL"` |
| PDF 文件 | `bash scripts/extract_pdf.sh "PATH"` |
| Web 搜索 | `bash scripts/search.sh "query"` |
| 其他 URL | `bash scripts/fetch.sh "URL"` |

## 依赖

- **基础**: bash, curl, python3
- **微信**: `pip install playwright beautifulsoup4 lxml && playwright install chromium`
- **飞书**: 设置 `FEISHU_APP_ID` + `FEISHU_APP_SECRET` 环境变量
- **PDF**: `pip install marker-pdf` 或 `brew install poppler`
- **搜索**: `npx open-websearch@latest`

## 相关技能

- presearch - 开发前搜索现有方案
