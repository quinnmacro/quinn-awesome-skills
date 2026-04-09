---
name: tear-sheet
description: |
  Generate company tear sheets (one-page profiles) using S&P Capital IQ data.
  Supports 4 audience types: Equity Research, IB/M&A, Corporate Development, Sales/BD.
  "公司简报", "企业概览", "公司介绍".
version: 1.0.0
author: quinnmacro
parent: spglobal
---

# Tear Sheet - 公司简报生成器

使用标普 Capital IQ 实时数据生成格式化的公司简报。

## What is a Tear Sheet?

Tear Sheet（公司简报）是一页式的公司概览文档，用于快速了解公司基本情况。名称来源于纸质时代——分析师从报告中"撕下"(tear off) 一页给客户或同事。

**核心用途:**
- 投资银行: Pitch book 中的公司介绍页
- 股票研究: 研究报告开头的公司概览
- 企业发展: 并购目标初筛
- 销售/BD: 客户会议前的快速了解

## Why It Matters

| 传统方式 | AI + MCP |
|----------|----------|
| 登录 Capital IQ → 搜索公司 → 复制数据 → 格式化 | 一条命令自动生成 |
| 30-60 分钟 | < 2 分钟 |
| 格式不一致 | 标准化输出 |
| 手动更新 | 实时数据 |

## Audience Types

不同的受众需要不同的信息重点：

### 1. Equity Research (股票研究)

**重点信息:**
- 估值指标 (P/E, P/B, EV/EBITDA)
- 盈利能力 (ROE, margins)
- 增长趋势 (revenue growth, EPS growth)
- 分析师评级和目标价
- 竞争对手对比

### 2. IB/M&A (投资银行/并购)

**重点信息:**
- 公司规模 (revenue, EBITDA)
- 估值区间 (交易倍数)
- 资本结构 (debt/equity)
- 股权结构 (主要股东)
- 历史交易记录

### 3. Corporate Development (企业发展)

**重点信息:**
- 战略定位
- 核心业务/产品
- 目标市场
- 技术栈/核心竞争力
- 潜在协同效应

### 4. Sales/BD (销售/业务拓展)

**重点信息:**
- 公司概况
- 关键决策人
- IT 预算
- 现有供应商
- 痛点/需求

## Workflow

### Step 1: Identify Company

```
用户输入:
- 公司名称: "Palantir", "苹果", "Microsoft"
- 或股票代码: "PLTR", "AAPL", "MSFT"
- 或 Capital IQ ID: "IQ247824"
```

### Step 2: Fetch Data via MCP

```
MCP 调用:
1. Company Profile - 基本信息
2. Financial Statements - 财务数据
3. Valuation Metrics - 估值指标
4. Ownership - 股权结构
5. Competitors - 竞争对手
```

### Step 3: Generate Tear Sheet

```
输出格式:
- Word 文档 (.docx)
- 或 Markdown (可转换为其他格式)
```

## Output Template

```markdown
# [公司名称] - Company Tear Sheet
## [股票代码] | [行业] | [市值]

---

### 公司概况
- **成立时间**: YYYY年
- **总部**: 城市, 国家
- **员工数**: X,XXX人
- **主营业务**: [一句话描述]

### 核心业务
| 业务线 | 收入占比 | 同比增长 |
|--------|----------|----------|
| 业务A | XX% | +XX% |
| 业务B | XX% | +XX% |

### 财务概要
| 指标 | TTM | YoY | QoQ |
|------|-----|-----|-----|
| 营业收入 | $X.XB | +X% | +X% |
| 毛利润 | $X.XB | +X% | +X% |
| 毛利率 | XX% | | |
| EBITDA | $X.XB | +X% | +X% |
| 净利润 | $X.XB | +X% | +X% |

### 估值指标
| 指标 | 当前 | 行业中位数 |
|------|------|-----------|
| P/E | XXx | XXx |
| EV/Revenue | XXx | XXx |
| EV/EBITDA | XXx | XXx |
| P/B | XXx | XXx |

### 股权结构
| 股东类型 | 持股比例 |
|----------|----------|
| 机构投资者 | XX% |
| 内部人士 | XX% |
| 公众流通 | XX% |

### 主要股东 (Top 5)
1. [机构名] - XX%
2. [机构名] - XX%
3. ...

### 竞争对手
| 公司 | 市值 | P/E | EV/EBITDA |
|------|------|-----|-----------|
| [竞对1] | $XXB | XXx | XXx |
| [竞对2] | $XXB | XXx | XXx |
| [竞对3] | $XXB | XXx | XXx |

### 分析师观点
- **共识评级**: 买入/持有/卖出
- **目标价**: $XXX (上涨空间 XX%)
- **覆盖分析师**: XX人

### 关键事件 (近12个月)
- [日期]: [事件描述]
- [日期]: [事件描述]

---

*数据来源: S&P Global Capital IQ | 生成时间: YYYY-MM-DD*
*免责声明: 仅供参考，不构成投资建议*
```

## Usage

```bash
# 基本用法
/tear-sheet Palantir

# 指定受众
/tear-sheet AAPL --audience equity-research
/tear-sheet Microsoft --audience ib-ma
/tear-sheet Tesla --audience corporate-development
/tear-sheet NVIDIA --audience sales-bd

# 指定输出格式
/tear-sheet 苹果 --format word
/tear-sheet Google --format markdown
```

## Best Practices

1. **受众定制**: 不同受众关注点不同，选择合适的 audience 参数
2. **时效性**: Tear Sheet 生成后，关键数据需标注时间戳
3. **可比性**: 竞争对手列表需验证行业相关性
4. **数据缺口**: 私有公司数据可能不完整，需明确标注

## Common Errors

### 公司识别错误

```
问题: 输入"苹果"可能匹配多家公司
解决: 使用股票代码 + 交易所 (AAPL-US) 或 Capital IQ ID
```

### 数据不完整

```
问题: 私有公司财务数据缺失
解决: 
1. 使用"部分数据"模式生成
2. 标注缺失字段为"N/A"
3. 补充公开信息来源
```

## Examples

### Example 1: Equity Research Tear Sheet

```
输入: /tear-sheet Palantir --audience equity-research

输出重点:
- 估值对比 (vs. 软件行业)
- 增长趋势 (收入、客户数)
- 分析师评级汇总
- 竞争对手矩阵
```

### Example 2: IB/M&A Tear Sheet

```
输入: /tear-sheet "某科技公司" --audience ib-ma

输出重点:
- 估值区间 (基于可比交易)
- 资本结构分析
- 股权结构 (潜在出售障碍)
- 历史交易记录
```

## Related Skills

- [funding-digest](../funding-digest/) - 融资摘要
- [earnings-preview](../earnings-preview/) - 业绩预览
- [earnings-analyzer](../../earnings-analyzer/) - 财报分析
