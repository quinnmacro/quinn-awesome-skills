---
name: funding-digest
description: |
  Generate industry funding and M&A transaction summaries using S&P Capital IQ data.
  Weekly/monthly deal flow reports for PE, VC, and M&A tracking.
  "融资摘要", "交易流", "Deal Flow", "并购动态".
version: 1.0.0
author: quinnmacro
parent: spglobal
---

# Funding Digest - 融资摘要生成器

使用标普 Capital IQ 交易数据生成行业融资和并购摘要。

## What is a Funding Digest?

Funding Digest（融资摘要/交易流摘要）是金融专业人士追踪特定行业或市场融资活动的周期性报告。

**核心用途:**
- PE/VC: 追踪投资机会和市场热度
- 投资银行: 了解并购交易动态
- 企业发展: 监控竞争对手融资状态
- LP: 了解市场资本流向

## Why It Matters

| 传统方式 | AI + MCP |
|----------|----------|
| 手动收集多来源数据 | 自动聚合 Capital IQ 交易数据 |
| Excel 整理，PowerPoint 制作 | 一键生成格式化报告 |
| 数小时工作量 | 分钟级完成 |
| 数据来源分散 | 单一权威来源 |

## Output Format

单页 PowerPoint 幻灯片，包含：

```
+-------------------------------------------------------------+
|  融资摘要 (Funding Digest)                                     |
|  [时间段] · [行业]                              [日期]         |
|--------------------------------------------------------------|
|  融资总额    轮次数    平均投前估值    最大轮次                   |
|  $X.XB      N        $X.XB         $X.XB                    |
|                                                              |
|  关键要点 (Key Takeaways)                                    |
|  1. ...  2. ...  3. ...                                      |
|                                                              |
|  重要交易 (Notable Deals)                                    |
|  公司 | 类型 | 公告日 | 金额 | 投前估值 | 投后估值             |
|  [页脚：数据来源：S&P Global Capital IQ | AI免责声明]          |
+-------------------------------------------------------------+
```

## Workflow

### Step 1: Define Scope

```
用户输入:
- 行业: "AI", "半导体", "fintech", "healthcare"
- 时间段: "weekly", "monthly", "quarterly"
- 地区: "China", "US", "Global", "SEA"
- 交易类型: "VC", "PE", "M&A", "All"
```

### Step 2: Fetch Transaction Data

```
MCP 调用:
1. 按行业筛选交易
2. 按时间段聚合
3. 提取关键交易详情
4. 计算汇总统计
```

### Step 3: Generate Report

```
输出:
- PowerPoint 幻灯片 (.pptx)
- 或 Markdown 表格
```

## Key Metrics

### Summary Statistics

| Metric | Description |
|--------|-------------|
| Total Funding | 融资总额 |
| Deal Count | 交易数量 |
| Avg Round Size | 平均轮次规模 |
| Avg Pre-money | 平均投前估值 |
| Largest Deal | 最大单笔交易 |

### Deal-Level Data

| Field | Description |
|-------|-------------|
| Company | 公司名称 |
| Round Type | 轮次类型 (A, B, Series...) |
| Amount | 融资金额 |
| Pre-money Valuation | 投前估值 |
| Post-money Valuation | 投后估值 |
| Lead Investors | 领投方 |
| Announcement Date | 公告日期 |
| Close Date | 交割日期 |

## China Market Specifics

中国市场融资摘要的特殊考虑：

### 1. 人民币 vs. 美元基金

```
区分追踪:
- 人民币基金投资 → A股/科创板退出路径
- 美元基金投资 → 海外/VIE架构退出
```

### 2. 政府引导基金

```
特殊标注:
- 国家大基金参与
- 地方政府引导基金
- 政策驱动 vs. 市场驱动
```

### 3. 监管因素

```
影响因素:
- 行业政策变化
- IPO 通道畅通度
- 外资准入限制
```

### 4. 数据透明度

```
常见问题:
- 估值未披露 (显示 "N/A")
- 金额仅为范围 (取中位数)
- 公告延迟 (标注日期差异)
```

## Usage

```bash
# 基本用法
/funding-digest AI行业
/funding-digest semiconductor --period weekly
/funding-digest fintech --region China --period monthly

# 指定交易类型
/funding-digest healthcare --deal-type M&A
/funding-digest "enterprise software" --deal-type VC

# 指定输出格式
/funding-digest AI --format pptx
/funding-digest AI --format markdown
```

## Output Template

```markdown
# [行业] 融资摘要
## [时间段] | [地区]

---

### 市场概览

| 指标 | 数值 | 环比 | 同比 |
|------|------|------|------|
| 融资总额 | $X.XB | +X% | +X% |
| 交易数量 | XX | +X | +X |
| 平均轮次 | $XXM | +X% | +X% |
| 最大轮次 | $XXXM | - | - |

### 关键要点

1. **[趋势标题]**: [描述]
2. **[趋势标题]**: [描述]
3. **[趋势标题]**: [描述]
4. **[趋势标题]**: [描述]

### 重要交易

| 公司 | 轮次 | 金额 | 估值 | 领投方 | 备注 |
|------|------|------|------|--------|------|
| [公司A] | B轮 | $XXM | $XXXM | [机构] | [亮点] |
| [公司B] | A轮 | $XXM | $XXM | [机构] | [亮点] |
| [公司C] | C轮 | $XXXM | $XB | [机构] | [亮点] |
| [公司D] | Pre-B | $XXM | N/A | [机构] | [亮点] |

### 细分领域分布

| 细分领域 | 交易数 | 融资额 | 占比 |
|----------|--------|--------|------|
| [领域A] | XX | $XXM | XX% |
| [领域B] | XX | $XXM | XX% |
| [领域C] | XX | $XXM | XX% |

### 投资人活跃度

| 投资机构 | 交易数 | 领投数 | 重点领域 |
|----------|--------|--------|----------|
| [机构A] | XX | XX | [领域] |
| [机构B] | XX | XX | [领域] |

---

*数据来源: S&P Global Capital IQ | 生成时间: YYYY-MM-DD*
*免责声明: 部分交易数据可能未完全披露，仅供参考*
```

## Best Practices

### 1. 时间段选择

```
高频行业 (AI, SaaS): weekly 或 bi-weekly
中频行业 (医疗, 金融): monthly
低频行业 (工业, 基建): quarterly
```

### 2. 公告日 vs. 交割日

```
推荐使用公告日:
- 更及时反映市场动态
- 避免重复计算

需同时标注交割状态:
- 已交割 (Closed)
- 进行中 (Pending)
```

### 3. 估值数据处理

```
估值披露率 > 50%: 显示平均值
估值披露率 < 50%: 显示中位数或标注"N/A"
```

## Common Errors

### 重复计算

```
问题: 同一交易在不同时间段重复出现
解决: 使用唯一交易ID去重
```

### 货币单位混乱

```
问题: 人民币和美元混合计算
解决: 分币种统计，合并时使用统一汇率
```

### 行业分类过窄

```
问题: 交易数量太少，无统计意义
解决: 扩大行业范围或延长时间段
```

## Examples

### Example 1: 中国 AI 行业周度摘要

```bash
/funding-digest AI --region China --period weekly
```

输出要点:
- 本周融资总额、轮次数
- 大模型 vs. 应用层分布
- 政府资金参与比例
- 美元基金活跃度

### Example 2: 全球半导体月度摘要

```bash
/funding-digest semiconductor --period monthly
```

输出要点:
- 设计/制造/设备/材料分布
- 地区分布 (China, US, Taiwan, Korea)
- 大额交易详情
- IPO/M&A 退出动态

## Related Skills

- [tear-sheet](../tear-sheet/) - 公司简报
- [earnings-preview](../earnings-preview/) - 业绩预览
- [investor-distiller](../../investor-distiller/) - 投资大师智慧
