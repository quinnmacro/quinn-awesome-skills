---
description: 生成业绩预览报告，包含共识预测、指引、分析师情绪
allowed-tools: Bash(curl *), Bash(python3 *), WebFetch
---

# /earnings-preview - 业绩预览

使用 S&P Capital IQ 数据生成财报发布前的预览报告。

## 用法

```bash
/earnings-preview <公司> [季度] [--focus <重点>]
```

## 参数

| 参数 | 说明 |
|------|------|
| `季度` | 如 2024Q4, upcoming, next |
| `--focus` | 关注重点: guidance, segments, margins |

## 示例

```bash
/earnings-preview AAPL
/earnings-preview Microsoft 2024Q4
/earnings-preview NVDA --quarter upcoming
/earnings-preview Tesla --focus guidance
```

## 输出内容

- 共识预测（营收、EPS、毛利率）
- 历史表现（Beat/Miss 记录）
- 公司指引（vs. 市场预期）
- 分析师情绪（评级分布、目标价）
- 关注主题（3-5 个核心看点）
- 敏感度分析

## 相关技能

- tear-sheet - 公司简报
- funding-digest - 融资摘要
- earnings-analyzer - 财报分析
