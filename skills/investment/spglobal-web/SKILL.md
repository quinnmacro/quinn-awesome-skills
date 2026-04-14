---
name: spglobal-web
description: |
  S&P Global Capital IQ 网页数据抓取（基于 Playwright）。
  直接抓取 Capital IQ 网页数据，无需 API 认证。
  使用已有的网页端权限，自动登录并提取数据。
  "标普全球", "Capital IQ", "S&P", "公司简报", "网页抓取".
version: 1.0.0
author: quinnmacro
requires:
  - Capital IQ Pro 网页端访问权限
  - playwright (uv tool install playwright && playwright install chromium)
layer: domain. Triggers: "标普全球", "Capital IQ", "S&P", "公司简报", "融资摘要", "业绩预览".
---

# S&P Global Web - Capital IQ 网页数据抓取

直接抓取 Capital IQ 网页数据，无需复杂的 API 认证。


## 一、快速开始

### 1.1 何时使用

- TODO: 添加触发场景

### 1.2 核心步骤

1. TODO: 步骤1
2. TODO: 步骤2

### 1.3 成功标准

- [ ] TODO: 验证标准

## 四、检查清单

### 执行前
- [ ] 前置条件检查

### 执行中
- [ ] 关键步骤验证

### 执行后
- [ ] 结果验证
## Why Web Scraping?

| API 方式 | 网页抓取 |
|----------|----------|
| 需要单独申请 Kensho 账号 | 使用已有的 Capital IQ 权限 |
| 复杂的 Okta/OAuth 认证 | 只需登录一次，保存浏览器状态 |
| Python 配置繁琐 | Playwright 自动化浏览器 |
| 额外费用 | 无额外费用 |

## Prerequisites

```bash
# 安装 Playwright
uv tool install playwright
playwright install chromium
```

## Workflow

### Step 1: 保存登录状态（首次使用）

```bash
uv run python ~/.claude/skills/spglobal-web/scripts/login.py
```

这会：
1. 打开 Capital IQ 登录页面
2. 等待你手动登录
3. 登录后关闭浏览器或等待 60 秒自动关闭
4. 登录状态自动保存在 `~/.spglobal/browser_profile/`

### Step 2: 使用技能

```bash
# 获取公司数据
uv run python ~/.claude/skills/spglobal-web/scripts/fetch_company.py AAPL

# 生成 Tear Sheet
uv run python ~/.claude/skills/spglobal-web/scripts/tear_sheet.py AAPL --output ~/Downloads/
```

## Features

| 功能 | 命令 | 输出 |
|------|------|------|
| 公司概况 | `fetch_company.py AAPL` | JSON |
| Tear Sheet | `tear_sheet.py AAPL` | Markdown/JSON |

## Data Sources

从 Capital IQ 网页抓取：

| 页面 | URL 模式 | 数据 |
|------|----------|------|
| Company Profile | `/company/{id}` | 基本信息、业务描述 |
| Financials | `/company/{id}/financials` | 三大财务报表 |
| Valuation | `/company/{id}/valuation` | 估值指标 |
| Peers | `/company/{id}/peers` | 可比公司 |

## Usage

### 在 Claude Code 中使用

```
/spglobal-web AAPL
/spglobal-web 苹果公司
/spglobal-web Microsoft --tear-sheet
```

### Python 直接调用

```python
# 使用持久化浏览器配置
from pathlib import Path
from playwright.sync_api import sync_playwright

PROFILE_DIR = Path.home() / ".spglobal" / "browser_profile"

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=str(PROFILE_DIR),
        headless=True
    )
    page = context.pages[0]
    page.goto("https://www.capitaliq.spglobal.com/company/AAPL")
    # 提取数据...
```

## Login Persistence

登录状态保存在 `~/.spglobal/browser_profile/`：

```
~/.spglobal/
├── browser_profile/    # 持久化浏览器配置（cookies、缓存等）
├── cache/              # 数据缓存
└── exports/            # 导出文件
```

**安全提示：**
- `browser_profile/` 包含敏感登录信息，不要分享
- 建议添加到 `.gitignore`
- 定期重新运行 login.py 更新登录状态

## Rate Limiting

为避免被封，请求间隔：

| 操作 | 间隔 |
|------|------|
| 页面请求 | 2-5 秒 |
| 批量查询 | 每批 10 个，间隔 30 秒 |

## Common Errors

### Error: 登录状态过期

```
解决方案: 重新运行 login.py 保存登录状态
```

### Error: 公司未找到

```
解决方案: 使用 Capital IQ 公司 ID (如 IQ123456)
或尝试不同搜索词
```

### Error: 页面加载超时

```
解决方案: 检查网络，或增加超时时间
```

## Related Skills

- [earnings-analyzer](../earnings-analyzer/) - 财报分析
- [investor-distiller](../investor-distiller/) - 投资大师智慧
- [spglobal](../spglobal/) - API 方式（需要 Kensho 账号）
