<div align="center">

# 🫧 Bloomberg AI Prompts

**Professional prompt templates for Bloomberg Terminal `{AKSB <GO>}`**

*Fixed Income • Currencies • Commodities • Credit • Equities*

**专业级 Bloomberg 终端 AI 分析模板**

*利率 • 外汇 • 大宗商品 • 信用 • 股票*

---

[![Bloomberg](https://img.shields.io/badge/Platform-Bloomberg_Terminal-blue?style=for-the-badge)](https://www.bloomberg.com/professional/solution/bloomberg-terminal/)
[![Templates](https://img.shields.io/badge/Templates-41-green?style=for-the-badge)]()
[![FICC](https://img.shields.io/badge/FICC-26_prompts-orange?style=for-the-badge)]()
[![Equity](https://img.shields.io/badge/Equity-15_templates-purple?style=for-the-badge)]()

</div>

---

## 📊 Quick Navigation | 快速导航

| Category | Templates | Description | 描述 |
|:--------:|:---------:|:------------|:-----|
| [🏢 **Equity**](#-equity-prompts--股票分析) | 15 | Company, Sector, Event, Market analysis | 公司、行业、事件、市场分析 |
| [📈 **FICC**](#-ficc-prompts--固收外汇商品) | 26 | Rates, FX, Credit, Commodities | 利率、外汇、信用、商品 |
| [⚡ **Mini Prompts**](#-mini-prompts--快速分析) | 14 | Quick daily analysis | 日常快速分析 |
| [🎭 **Theme Prompts**](#-theme-prompts--主题分析) | 7 | Macro scenario analysis | 宏观场景分析 |

---

## 🏢 Equity Prompts | 股票分析

> **Company & Sector Analysis for Investment Decisions**
> 
> **公司及行业分析，支持投资决策**

### 📋 Template Index | 模板索引

#### 🏭 Company | 公司视角 (4 templates)

| Template | Use Case | 用途 | Variable |
|:---------|:---------|:-----|:---------|
| [Trends Analysis](company/trends-analysis/template.md) | Stock + Financial + Operational trends | 股价+财务+运营趋势 | `{Company/Ticker}` |
| [Management & Governance](company/management-governance/template.md) | Board & leadership assessment | 治理+管理层评估 | `{Company/Ticker}`, `N` |
| [Company Snapshot](company/company-snapshot/template.md) | Investment thesis primer | 投资概览手册 | `{Company/Ticker}` |
| [Performance Tracker](company/performance-tracker/template.md) | Quarterly financial tracking | 季度财务追踪 | `{Company/Ticker}`, `N` |

#### 🏭 Sector | 行业视角 (3 templates)

| Template | Use Case | 用途 | Variable |
|:---------|:---------|:-----|:---------|
| [Sector Snapshot](sector/sector-snapshot/template.md) | Industry + peer comparison | 行业+同行对比 | `{Sector Name}` |
| [Sector Rotation](sector/sector-rotation/template.md) | Leading/lagging sector signals | 行业轮动信号 | `{Region/Market}` |
| [Sector Valuation](sector/sector-valuation/template.md) | P/E, EV/EBITDA cross-sector | 行业估值对比 | `{Region/Market}` |

#### ⚡ Event | 事件视角 (4 templates)

| Template | Use Case | 用途 | Variable |
|:---------|:---------|:-----|:---------|
| [Breaking Event](event/breaking-event/template.md) | Material event analysis (24-96h) | 突发事件分析 | `{Company/Ticker}` |
| [Earnings Event](event/earnings-event/template.md) | Quarterly results surprise | 业绩发布分析 | `{Company/Ticker}` |
| [Regulatory Event](event/regulatory-event/template.md) | FDA/SEC/DOJ impact assessment | 监管事件分析 | `{Company/Ticker}` |
| [M&A Event](event/ma-event/template.md) | Deal structure + synergy | 并购事件分析 | `{Company/Ticker}` |

#### 📊 Market | 市场视角 (4 templates)

| Template | Use Case | 用途 | Variable |
|:---------|:---------|:-----|:---------|
| [Credit Strategy](market/credit-strategy/template.md) | Credit market morning briefing | 信用市场早报 | `{Market}` |
| [Equity Brief](market/equity-brief/template.md) | Index + sector + movers | 股票市场简报 | `{Region/Market}` |
| [FX Review](market/fx-review/template.md) | G10 + EM FX + carry | 外汇市场回顾 | `{Currency/Region}` |
| [Volatility Review](market/volatility-review/template.md) | Cross-asset vol regime | 波动率回顾 | `{Market/Region}` |

### 🎯 Usage | 使用方法

**English:**
```
1. Bloomberg Terminal → {AKSB <GO>}
2. Copy template → Replace variables
3. Example: {Company/Ticker} → AAPL US Equity
```

**中文:**
```
1. Bloomberg 终端 → 输入 {AKSB <GO>}
2. 复制模板 → 替换变量
3. 示例: {Company/Ticker} → AAPL US Equity
```

<details>
<summary>📖 Variable Format Guide | 变量格式指南</summary>

| Variable | Format | Example | 示例 |
|----------|--------|---------|------|
| `{Company/Ticker}` | Bloomberg Ticker | `AAPL US Equity` | `700 HK Equity` |
| `{Sector Name}` | Industry Name | `Technology` | `Healthcare` |
| `{Market}` | Market Type | `US IG`, `Asia HY` | `EM USD` |
| `N` | Period Count | `4`, `8` | 周期数 |

**Data Period Rules | 数据周期规则:**

| Rule | Description | 说明 |
|------|-------------|------|
| N+1 | Extra period for YoY calc | YoY计算需额外1期 |
| N+5 | Performance Tracker requirement | Performance Tracker最严格 |
| < 366 days | Data freshness priority | 数据新鲜度优先级 |

</details>

---

## 📈 FICC Prompts | 固收外汇商品

> **Fixed Income, Currencies & Commodities Analysis**
> 
> **利率、外汇、信用与大宗商品分析**

### 🔥 Core Templates (5) | 核心模板

| Template | 类别 | Key Metrics | 关键指标 |
|:---------|:----:|:------------|:---------|
| [Sovereign Yields](ficc/rates/sovereign-yields/template.md) | 📉 Rates | Yield curve + CB policy | 收益率曲线 + 央行定价 |
| [Currency Cross](ficc/fx/currency-cross/template.md) | 💱 FX | Spot/Forward + Carry + Vol | 即远期 + Carry + 波动率 |
| [Credit Spreads](ficc/credit/spreads/template.md) | 💳 Credit | IG vs HY + Sector matrix | IG/HY利差 + 行业矩阵 |
| [Energy Futures](ficc/commodities/energy-futures/template.md) | 🛢️ Comm. | Curve structure + OVX | 曲线结构 + OVX波动率 |
| [Cross-Asset](ficc/cross-asset/template.md) | 🔗 Multi | Transmission chains | 跨资产传导链 |

### 📚 FICC Documentation | 文档资源

| Document | Content | 内容 |
|:---------|:--------|:-----|
| [📖 Design Framework](ficc/FICC-DESIGN.md) | Strategy types + Methodology | 策略类型 + 方法论 |
| [🔍 Quick Reference](ficc/QUICK-REFERENCE.md) | Ticker lookup + BQL templates | Ticker速查 + BQL模板 |
| [💡 Trader Tips](ficc/TRADER-TIPS.md) | Pitfalls + Formulas + Jargon | 坑点 + 公式 + 黑话 |
| [📋 Case Studies](ficc/CASE-STUDIES.md) | 7 real & scenario examples | 7个真实+虚构案例 |

### 🎯 FICC by Strategy Type | 策略类型

| Strategy | Description | 描述 |
|:---------|:------------|:-----|
| **Curve Trade** | Steepener / Flattener | 曲线交易：做陡/做平 |
| **Carry Trade** | Harvest yield differential | Carry交易：赚取利差 |
| **Calendar Spread** | Commodity time spreads | 日历价差：时间套利 |
| **Cross-Market** | Regional spread arbitrage | 跨市场套利 |
| **Vol Trade** | Long/Short volatility | 波动率交易 |

### 📊 Key Tickers | 关键Ticker

| Asset | Ticker | Description |
|:------|:-------|:------------|
| US 10Y | `GT10 Govt` | 美国国债10年期 |
| EUR 10Y | `GTDEM10Y Govt` | 德国国债10年期 |
| WTI Crude | `CL1 Comdty` | WTI原油近月 |
| US IG Credit | `LCGDTRUU Index` | 美国投资级信用债 |
| US HY Credit | `HLHO Index` | 美国高收益信用债 |
| VIX | `VIX Index` | 标普500波动率 |
| OVX | `OVX Index` | 原油波动率 |

---

## ⚡ Mini Prompts | 快速分析

> **Quick Analysis for Daily Workflow**
> 
> **日常快速分析工具**

### 📅 Daily Workflow | 日常流程

| Prompt | Use When | 场景 | Time |
|:-------|:---------|:-----|:----:|
| **Pre-Market Scan** | Before market open | 开盘前扫描 | 5 min |
| **Close Review** | End of trading day | 收盘复盘 | 10 min |
| **Weekly Wrap** | Friday close | 周度总结 | 15 min |

### ⚡ Event-Driven | 事件驱动

| Prompt | Trigger | 触发条件 |
|:-------|:--------|:---------|
| **Rate Decision Reaction** | CB meeting outcome | 央行决议结果 |
| **Geopolitical Shock** | War, sanctions, election | 战争、制裁、选举 |
| **Data Release Reaction** | CPI, NFP, GDP surprise | CPI/NFP/GDP意外 |

### 📊 Relative Value | 相对价值

| Prompt | Use Case | 用途 |
|:-------|:---------|:-----|
| **Curve Trade Setup** | Steepener/Flattener ideas | 曲线交易设置 |
| **Credit RV** | IG vs HY relative value | IG/HY相对价值 |
| **FX Carry Trade** | Carry attractiveness | FX Carry评估 |

### 🛡️ Risk & Stress | 风险压力

| Prompt | Purpose | 用途 |
|:-------|:--------|:-----|
| **Market Stress Check** | Cross-asset stress level | 跨资产压力检查 |
| **Liquidity Assessment** | Market functioning check | 流动性评估 |
| **Position Risk Check** | VaR + Stop-loss sizing | 持仓风险评估 |

---

## 🎭 Theme Prompts | 主题分析

> **Macro-Driven Scenario Analysis**
> 
> **宏观驱动的场景分析**

| Theme | When to Use | 使用场景 |
|:------|:------------|:---------|
| 🌡️ **Inflation Trade** | CPI surprises, breakeven moves | CPI意外、breakeven变动 |
| 📉 **Recession Trade** | Curve inversion, LEI decline | 曲线倒挂、LEI下降 |
| 💧 **Liquidity Crisis** | Bid-ask widening, market freeze | 价差扩大、市场冻结 |
| ⚖️ **CB Divergence** | Rate differential widening | 利率差扩大 |
| ❌ **Policy Mistake** | Real rates extreme | 实际利率极端 |
| 📊 **Tail Risk** | Geopolitical escalation | 地缘政治升级 |
| 🦢 **Black Swan Prep** | Portfolio resilience check | 组合韧性检查 |

---

## 🗂️ Directory Structure | 目录结构

```
bloomberg/
│
├── 📄 README.md                    # This file | 本文件
│
├── 🏢 company/                     # Equity - Company | 股票-公司 (4)
│   ├── trends-analysis/            # 趋势分析
│   ├── management-governance/      # 治理评估
│   ├── company-snapshot/           # 投资概览
│   └── performance-tracker/        # 财务追踪
│
├── 🏭 sector/                      # Equity - Sector | 股票-行业 (3)
│   ├── sector-snapshot/            # 行业快照
│   ├── sector-rotation/            # 行业轮动
│   └── sector-valuation/           # 行业估值
│
├── ⚡ event/                       # Equity - Event | 股票-事件 (4)
│   ├── breaking-event/             # 突发事件
│   ├── earnings-event/             # 业绩发布
│   ├── regulatory-event/           # 监管事件
│   └── ma-event/                   # 并购事件
│
├── 📊 market/                      # Market-wide | 市场层面 (4)
│   ├── credit-strategy/            # 信用策略
│   ├── equity-brief/               # 股票简报
│   ├── fx-review/                  # 外汇回顾
│   └── volatility-review/          # 波动率回顾
│
└── 📈 ficc/                        # FICC Prompts | 固收外汇商品 (26)
    ├── README.md                   # FICC索引
    ├── FICC-DESIGN.md              # 设计框架
    ├── QUICK-REFERENCE.md          # 快速参考
    ├── MINI-PROMPTS.md             # 快速分析
    ├── CASE-STUDIES.md             # 案例研究
    ├── THEME-PROMPTS.md            # 主题分析
    ├── TRADER-TIPS.md              # 交易员技巧
    │
    ├── rates/sovereign-yields/     # 利率-国债
    ├── fx/currency-cross/          # 外汇-货币对
    ├── credit/spreads/             # 信用-利差
    ├── commodities/energy-futures/ # 商品-能源
    └── cross-asset/                # 跨资产
```

---

## 🚀 Quick Start | 快速开始

### First Time | 首次使用

```bash
# Clone the repository | 克隆仓库
git clone https://github.com/quinnmacro/quinn-awesome-skills.git

# Navigate to Bloomberg prompts | 进入目录
cd quinn-awesome-skills/skills/external/bloomberg
```

### Using a Template | 使用模板

```
Step 1: Open template file | 打开模板文件
Step 2: Copy to Bloomberg Terminal {AKSB <GO>} | 复制到终端
Step 3: Replace variables | 替换变量
        {Company/Ticker} → AAPL US Equity
Step 4: Run analysis | 执行分析
```

---

## 📊 Stats | 统计

| Metric | Count | 指标 | 数量 |
|:-------|------:|:-----|-----:|
| Total Templates | 41 | 模板总数 | 41 |
| FICC Prompts | 26 | FICC提示词 | 26 |
| Equity Templates | 15 | 股票模板 | 15 |
| • Company | 4 | 公司模板 | 4 |
| • Sector | 3 | 行业模板 | 3 |
| • Event | 4 | 事件模板 | 4 |
| • Market | 4 | 市场模板 | 4 |
| Mini Prompts | 14 | 快速分析 | 14 |
| Theme Prompts | 7 | 主题分析 | 7 |
| Case Studies | 7 | 案例研究 | 7 |
| Documentation Pages | 11 | 文档页数 | 11 |

---

## 📜 Template Sources | 模板来源

| Source | Templates | 来源 | 数量 |
|:-------|:---------:|:-----|:----:|
| Bloomberg Official | 6 | Bloomberg官方 | 6 |
| Custom (Quinn-Written) | 9 | 自写模板 | 9 |

---

## 🔗 Related Resources | 相关资源

| Resource | Link |
|:---------|:-----|
| Bloomberg Terminal | [bloomberg.com](https://www.bloomberg.com/professional/solution/bloomberg-terminal/) |
| Wind Prompts | [../wind/](../wind/) *(Coming Soon)* |
| quinn-awesome-skills | [GitHub](https://github.com/quinnmacro/quinn-awesome-skills) |

---

## ⚠️ Notes | 注意事项

| Note | Description |
|:-----|:------------|
| **Terminal Required** | Templates require Bloomberg Terminal with data access |
| **DAPI Fields** | Some templates have strict DAPI field requirements |
| **Data Freshness** | Stale data (>180/366 days) should move to Historical section |
| **Credit Strategy** | Contains 70+ Bloomberg Index tickers |

| 注意 | 说明 |
|:-----|:-----|
| **终端必需** | 模板需在Bloomberg终端内使用，依赖数据API |
| **DAPI字段** | 部分模板有严格的字段限制 |
| **数据新鲜度** | 过期数据应移至历史数据部分 |
| **Credit Strategy** | 包含70+个Bloomberg指数ticker |

---

<div align="center">

**Made with 💙 for FICC & Equity Traders**

**用 💙 为固收外汇商品与股票交易员打造**

*Star ⭐ this repo if you find it useful!*

*觉得有用请点个 Star ⭐！*

[⬆ Back to Top | 返回顶部](#-bloomberg-ai-prompts)

</div>
