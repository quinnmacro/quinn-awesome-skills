---
description: 生成公司简报 (Tear Sheet)，支持股票研究/投行/企发/销售四种受众
allowed-tools: Bash(curl *), Bash(python3 *), WebFetch
---

# /tear-sheet - 公司简报生成器

使用 S&P Capital IQ 数据生成一页式公司概览。

## 用法

```bash
/tear-sheet <公司名称或股票代码> [--audience <类型>]
```

## 受众类型

| 类型 | 说明 |
|------|------|
| `equity-research` | 股票研究分析师 |
| `ib-ma` | 投资银行/并购 |
| `corporate-development` | 企业发展 |
| `sales-bd` | 销售/业务拓展 |

## 示例

```bash
/tear-sheet Palantir --audience equity-research
/tear-sheet AAPL --audience ib-ma
/tear-sheet Microsoft --audience sales-bd
/tear-sheet 苹果
```

## 输出内容

- 公司概况（成立时间、总部、员工、主营业务）
- 财务概要（营收、利润、毛利率）
- 估值指标（P/E, EV/EBITDA, P/B）
- 股权结构（机构/内部人士/公众）
- 竞争对手对比
- 分析师评级和目标价

## 相关技能

- funding-digest - 融资摘要
- earnings-preview - 业绩预览
