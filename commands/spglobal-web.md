---
description: S&P Capital IQ 网页数据抓取（基于 Playwright）
allowed-tools: Bash(python3 *), Bash(python *)
---

# /spglobal-web

直接从 Capital IQ 网页抓取数据，无需 API 认证。

## 用法

```
/spglobal-web <ticker>           # 获取公司数据
/spglobal-web <ticker> --tear    # 生成 Tear Sheet
/spglobal-web login              # 保存登录状态
```

## 工作流

<Steps>
1. 检查登录状态 (~/.spglobal/auth.json)
2. 如果未登录，提示运行 `python login.py`
3. 使用 Playwright 打开 Capital IQ 页面
4. 提取数据并返回
</Steps>

## 示例

### 首次使用（保存登录）

```bash
python ~/.claude/skills/spglobal-web/scripts/login.py
```

### 获取公司数据

```bash
python ~/.claude/skills/spglobal-web/scripts/fetch_company.py AAPL
```

### 生成 Tear Sheet

```bash
python ~/.claude/skills/spglobal-web/scripts/tear_sheet.py MSFT --output ~/Downloads/
```

## 相关技能

- [spglobal](../skills/investment/spglobal/) - API 方式（需要 Kensho 账号）
- [earnings-analyzer](../skills/investment/earnings-analyzer/) - 财报分析
