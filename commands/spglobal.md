---
description: S&P Global 数据集成 - 公司简报、融资摘要、业绩预览
allowed-tools: Bash(curl *), Bash(python3 *), WebFetch
---

# /spglobal - S&P Global 数据集成

使用标普 Capital IQ 实时数据生成金融研究报告。

## 子命令

| 命令 | 功能 |
|------|------|
| `/tear-sheet` | 公司简报 |
| `/funding-digest` | 融资摘要 |
| `/earnings-preview` | 业绩预览 |

## 用法

```bash
# 公司简报
/tear-sheet Palantir --audience equity-research
/tear-sheet 苹果 --audience ib-ma

# 融资摘要
/funding-digest AI行业 --period weekly
/funding-digest semiconductor --region China

# 业绩预览
/earnings-preview AAPL 2024Q4
/earnings-preview NVDA --quarter upcoming
```

## 配置要求

需要 S&P Global API Key：

```bash
export SPGLOBAL_API_KEY="your_key"
```

## 相关技能

- earnings-analyzer - 财报分析
- investor-distiller - 投资大师智慧
- macro-brief - 宏观经济简报
