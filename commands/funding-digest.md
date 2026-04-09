---
description: 生成行业融资/并购摘要，追踪市场资本流向
allowed-tools: Bash(curl *), Bash(python3 *), WebFetch
---

# /funding-digest - 融资摘要

使用 S&P Capital IQ 交易数据生成行业融资和并购摘要。

## 用法

```bash
/funding-digest <行业> [--period <时间段>] [--region <地区>] [--deal-type <类型>]
```

## 参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--period` | 时间段: weekly, monthly, quarterly | weekly |
| `--region` | 地区: China, US, Global, SEA | Global |
| `--deal-type` | 类型: VC, PE, M&A, All | All |

## 示例

```bash
/funding-digest AI行业
/funding-digest semiconductor --period monthly
/funding-digest fintech --region China
/funding-digest healthcare --deal-type M&A
```

## 输出内容

- 市场概览统计（融资总额、交易数、平均规模）
- 关键要点（趋势洞察）
- 重要交易明细
- 细分领域分布
- 投资人活跃度

## 相关技能

- tear-sheet - 公司简报
- earnings-preview - 业绩预览
