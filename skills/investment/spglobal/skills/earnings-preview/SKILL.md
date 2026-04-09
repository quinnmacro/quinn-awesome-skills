---
name: earnings-preview
description: |
  Generate structured earnings preview reports using S&P Capital IQ data.
  Includes consensus estimates, guidance, analyst sentiment, key themes.
  "业绩预览", "财报前瞻", "Earnings Preview".
version: 1.0.0
author: quinnmacro
parent: spglobal
---

# Earnings Preview - 业绩预览

使用标普 Capital IQ 数据生成结构化的业绩预览报告。

## What is an Earnings Preview?

Earnings Preview（业绩预览）是财报发布前准备的研究报告，帮助分析师和投资者了解市场预期和关注重点。

**核心用途:**
- 股票研究: 财报发布前的准备工作
- 投资管理: 调整仓位预期
- 企业 IR: 了解市场预期
- 销售/交易: 客户沟通素材

## Why It Matters

| 传统方式 | AI + MCP |
|----------|----------|
| 手动收集分析师预测 | 自动获取共识估计 |
| 多终端查询指引信息 | 单一来源聚合数据 |
| Excel 计算差异 | 自动计算 beat/miss |
| 2-4 小时准备 | 分钟级生成 |

## Report Structure

典型的业绩预览报告包含 4-5 页：

1. **Executive Summary** - 执行摘要
2. **Consensus Estimates** - 共识预测
3. **Guidance & Expectations** - 公司指引
4. **Analyst Sentiment** - 分析师情绪
5. **Key Themes to Watch** - 关注主题

## Workflow

### Step 1: Identify Company & Quarter

```
用户输入:
- 公司: "AAPL", "苹果", "Microsoft"
- 季度: "2024Q4", "upcoming", "next"
```

### Step 2: Fetch Data via MCP

```
MCP 调用:
1. Consensus Estimates - 分析师一致预测
2. Historical Results - 历史业绩
3. Company Guidance - 公司指引
4. Analyst Ratings - 分析师评级
5. Recent News - 近期新闻/事件
```

### Step 3: Generate Report

```
输出:
- 研究报告格式 (Markdown/Word)
- 包含图表和数据表格
```

## Key Data Points

### Consensus Estimates

| Metric | Description |
|--------|-------------|
| Revenue Estimate | 营收预测 |
| EPS Estimate | 每股收益预测 |
| EBITDA Estimate | EBITDA 预测 |
| Gross Margin Est. | 毛利率预测 |
| Estimate Revisions | 预测调整趋势 |

### Historical Comparison

| Metric | Description |
|--------|-------------|
| YoY Growth | 同比增长 |
| QoQ Growth | 环比增长 |
| Beat/Miss History | 历史 beat/miss 记录 |
| Surprise % | 意外幅度 |

### Guidance

| Metric | Description |
|--------|-------------|
| Revenue Guidance | 营收指引 |
| EPS Guidance | EPS 指引 |
| Margin Guidance | 利润率指引 |
| Capex Guidance | 资本开支指引 |

### Analyst Sentiment

| Metric | Description |
|--------|-------------|
| Consensus Rating | 一致评级 |
| Target Price | 目标价 |
| Rating Changes | 评级变化 |
| Estimate Trend | 预测趋势 |

## Output Template

```markdown
# [公司名称] [季度] 业绩预览
## 股票代码: [TICKER] | 行业: [Industry] | 报告日期: [Date]

---

## 执行摘要

[公司名称] 将于 [日期] 发布 [季度] 财报。市场预期营收 [$$]B，EPS $[.]。

**核心观点:**
- [观点1: 如 "收入增长预期稳健，关注云业务增速"]
- [观点2: 如 "毛利率压力持续，需关注成本控制"]
- [观点3: 如 "新管理层首次财报，指引成为关键"]

---

## 共识预测

### 关键指标预测

| 指标 | 共识预测 | 上期实际 | 同比 | 环比 |
|------|----------|----------|------|------|
| 营业收入 | $X.XXB | $X.XXB | +X% | +X% |
| EPS | $X.XX | $X.XX | +X% | +X% |
| 毛利率 | XX% | XX% | | |
| EBITDA | $X.XB | $X.XB | +X% | +X% |

### 分业务预测

| 业务线 | 预测收入 | 同比 | 占比 |
|--------|----------|------|------|
| 业务A | $X.XB | +X% | XX% |
| 业务B | $X.XB | +X% | XX% |
| 业务C | $X.XB | +X% | XX% |

---

## 历史表现

### 过去 4 季度 Beat/Miss

| 季度 | 营收预测 | 实际 | 差异% | EPS预测 | 实际 | 差异% |
|------|----------|------|-------|---------|------|-------|
| [Q] | $X.XB | $X.XB | +X% | $X.XX | $X.XX | +X% |
| [Q] | $X.XB | $X.XB | -X% | $X.XX | $X.XX | +X% |
| [Q] | $X.XB | $X.XB | +X% | $X.XX | $X.XX | -X% |
| [Q] | $X.XB | $X.XB | +X% | $X.XX | $X.XX | +X% |

**历史趋势:**
- 过去 4 季度 beat 率: XX%
- 平均意外幅度: +X.X%

---

## 公司指引

### 本季度指引

| 指标 | 指引范围 | 中位数 | 共识预测 | 隐含差异 |
|------|----------|--------|----------|----------|
| 营收 | $X-XB | $X.XB | $X.XB | +X% |
| EPS | $X.X-$X.X | $X.XX | $X.XX | -X% |

### 下季度/全年指引预期

| 指标 | 当前共识 | 上次指引 | 变化 |
|------|----------|----------|------|
| 全年营收 | $XXB | $XXB | +X% |
| 全年EPS | $X.XX | $X.XX | +X% |

---

## 分析师情绪

### 评级分布

| 评级 | 数量 | 占比 |
|------|------|------|
| 买入 | XX | XX% |
| 持有 | XX | XX% |
| 卖出 | XX | XX% |

**共识评级**: [买入/持有/卖出]

### 目标价

| 指标 | 数值 |
|------|------|
| 平均目标价 | $XXX |
| 最高目标价 | $XXX |
| 最低目标价 | $XXX |
| 隐含上涨空间 | XX% |

### 近期预测调整

| 方向 | 过去30天 | 过去90天 |
|------|----------|----------|
| 上调 | XX | XX |
| 下调 | XX | XX |
| 维持 | XX | XX |

---

## 关注主题

### 核心关注点

1. **[主题1: 如 "云业务增速"]**
   - 背景: [描述]
   - 市场预期: [预期]
   - 关键指标: [具体指标]
   - 潜在影响: [影响]

2. **[主题2: 如 "毛利率趋势"]**
   - 背景: [描述]
   - 市场预期: [预期]
   - 关键指标: [具体指标]
   - 潜在影响: [影响]

3. **[主题3: 如 "新管理层指引"]**
   - 背景: [描述]
   - 市场预期: [预期]
   - 关键指标: [具体指标]
   - 潜在影响: [影响]

### 敏感度分析

| 情景 | 营收 | EPS | 股价影响 |
|------|------|-----|----------|
| Bull Case | $X.XB (+X%) | $X.XX (+X%) | +X% |
| Base Case | $X.XB | $X.XX | 0% |
| Bear Case | $X.XB (-X%) | $X.XX (-X%) | -X% |

---

## 近期事件

| 日期 | 事件 | 潜在影响 |
|------|------|----------|
| [Date] | [事件描述] | [影响分析] |
| [Date] | [事件描述] | [影响分析] |

---

## 附录

### 分析师覆盖详情

| 机构 | 分析师 | 评级 | 目标价 | EPS预测 |
|------|--------|------|--------|---------|
| [机构] | [姓名] | 买入 | $XXX | $X.XX |
| [机构] | [姓名] | 持有 | $XXX | $X.XX |

---

*数据来源: S&P Global Capital IQ | 生成时间: YYYY-MM-DD*
*免责声明: 仅供参考，不构成投资建议*
```

## Usage

```bash
# 基本用法
/earnings-preview AAPL
/earnings-preview Microsoft 2024Q4

# 指定即将到来的季度
/earnings-preview GOOGL --quarter upcoming
/earnings-preview Tesla --quarter next

# 指定关注重点
/earnings-preview NVDA --focus guidance
/earnings-preview AMD --focus segments

# 指定输出格式
/earnings-preview AAPL --format word
/earnings-preview AAPL --format markdown
```

## Best Practices

### 1. 时间点选择

```
财报前 1-2 周: 生成预览报告
财报前 1-3 天: 更新预测变化
财报当天: 准备实时对比模板
```

### 2. 关注主题选择

```
选择 3-5 个核心主题:
- 市场最关心的指标
- 公司战略重点
- 行业趋势变化
- 管理层变动影响
```

### 3. 指引分析

```
比较指引与共识:
- 指引高于共识: 管理层乐观
- 指引低于共识: 管理层保守
- 指引符合共识: 市场定价合理
```

## Common Errors

### 季度识别错误

```
问题: 公司财年与日历年不一致
解决: 使用公司财年 (如 AAPL FY2024 Q1)
```

### 预测数据过时

```
问题: 分析师预测未及时更新
解决: 标注预测更新日期，重要变化需手动验证
```

### 指引缺失

```
问题: 部分公司不提供详细指引
解决: 使用历史趋势推断，明确标注假设
```

## Examples

### Example 1: 苹果 FY2024 Q4 预览

```bash
/earnings-preview AAPL FY2024Q4
```

关注重点:
- iPhone 16 销量首季度
- 服务收入增速
- 中国市场表现
- 毛利率指引

### Example 2: NVIDIA 即将发布财报

```bash
/earnings-preview NVDA --quarter upcoming
```

关注重点:
- Data Center 收入 (AI芯片需求)
- Blackwell 芯片进度
- 毛利率趋势
- 2025 年指引

## Related Skills

- [tear-sheet](../tear-sheet/) - 公司简报
- [funding-digest](../funding-digest/) - 融资摘要
- [earnings-analyzer](../../earnings-analyzer/) - 财报分析
