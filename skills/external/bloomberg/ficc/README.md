# FICC Prompts — Bloomberg AI

> Fixed Income, Currencies, Commodities 专属 prompts 集合

---

## 文档索引

| 文档 | 内容 | 版本 |
|------|------|------|
| [FICC-DESIGN.md](FICC-DESIGN.md) | 设计思路 + 策略框架 + 实战案例方法论 | v0.4 |
| [QUICK-REFERENCE.md](QUICK-REFERENCE.md) | Ticker速查 + BQL模板 + 函数速查 + 数据源 | v0.4 |
| [MINI-PROMPTS.md](MINI-PROMPTS.md) | 14个场景化快速分析 prompts | v0.2 |
| [CASE-STUDIES.md](CASE-STUDIES.md) | 7个实战案例 (真实测试 + 虚构场景) | v0.1 |
| [THEME-PROMPTS.md](THEME-PROMPTS.md) | 7个宏观主题分析 prompts | v0.1 |
| [TRADER-TIPS.md](TRADER-TIPS.md) | 交易员实战技巧 + 坑点 + 公式 + 黑话 | v0.1 |

---

## 主要模板 (5个)

| 视角 | 模板 | 变量 | 测试状态 |
|------|------|------|----------|
| **Rates** | [sovereign-yields](rates/sovereign-yields/) | `{Country/Currency}` | ✓ 已测试优化 |
| **FX** | [currency-cross](fx/currency-cross/) | `{Currency Pair}` | 待测试 |
| **Credit** | [spreads](credit/spreads/) | `{Market/Region}` | 待测试 |
| **Commodities** | [energy-futures](commodities/energy-futures/) | `{Commodity}` | ✓ 已测试优化 |
| **Cross-Asset** | [cross-asset](cross-asset/) | `{Theme}` | 待测试 |

---

## Mini Prompts (14个)

| 类别 | Prompts |
|------|---------|
| **Daily Workflow** (3) | Pre-Market Scan, Close Review, Weekly Wrap |
| **Event-Driven** (3) | Rate Decision, Geopolitical Shock, Data Release |
| **Relative Value** (3) | Curve Trade, Credit RV, FX Carry |
| **Risk & Stress** (3) | Market Stress Check, Liquidity, Position Risk |
| **Calendar** (2) | Economic Data, Central Bank Calendar |

---

## Theme Prompts (7个)

| 主题 | 适用场景 |
|------|----------|
| **Inflation Trade** | CPI surprises, breakeven moves |
| **Recession Trade** | Curve inversion, LEI decline |
| **Liquidity Crisis** | Bid-ask widening, market freeze |
| **CB Divergence** | Rate differential widening |
| **Policy Mistake** | Real rates extreme, guidance gap |
| **Tail Risk** | Geopolitical escalation, extreme events |
| **Black Swan Prep** | Portfolio resilience check |

---

## 实战案例 (7个)

| 案例 | 类型 | 核心洞察 |
|------|------|----------|
| EUR Sovereign Yields | 真实测试 | Bear steepening, ECB定价偏离, FX-linkage失效 |
| WTI Energy Futures | 真实测试 | 极端backwardation, Hormuz冲击, 正roll yield |
| Fed鹰派惊喜 | 虚构场景 | 曲线flatten, USD暴涨, risk-off传导 |
| OPEC意外增产 | 虚构场景 | Backwardation崩塌, vol crush |
| 中国信用危机 | 虚构场景 | EM contagion, 政策干预逆转 |
| EUR曲线Steepener | RV案例 | Mean reversion交易 +24bp |
| AUD/USD Carry | RV案例 | Carry不足以抵消spot下跌 |

---

## 交易员技巧

| 内容 | 描述 |
|------|------|
| **思维差异** | FICC vs Equity的根本区别 |
| **常见坑点** | Carry/Curve/Credit trade陷阱 |
| **快速判断** | VIX/OVX/Curve/IG-HY ratio阈值 |
| **数据日策略** | 发布前后时机把握 |
| **实用公式** | Carry/Vol/Break-even/DV01计算 |
| **黑话翻译** | Bid/Offer/Whack/Fade等术语 |
| **技能树** | Level 1-5 进阶路径 |

---

## 测试进度

| 模板 | 版本 | 状态 | 关键发现 |
|------|------|------|----------|
| sovereign-yields | v0.2 | ✓ 已测试 | MTD/YTD需BQL，EUR-JPY spread N/A |
| energy-futures | v0.1 | ✓ 已测试 | 添加OVX波动率，输出质量好 |
| currency-cross | v0.1 | 待测试 | - |
| spreads | v0.1 | 待测试 | - |
| cross-asset | v0.1 | 待测试 | - |

---

## 目录结构

```
ficc/
├── README.md                     # 总索引
├── FICC-DESIGN.md                # 设计思路 + 策略框架
├── QUICK-REFERENCE.md            # Ticker速查 + 函数速查
├── MINI-PROMPTS.md               # 14个场景prompts
├── CASE-STUDIES.md               # 实战案例集
├── THEME-PROMPTS.md              # 宏观主题prompts
├── TRADER-TIPS.md                # 交易员技巧
│
├── rates/sovereign-yields/       # 国债收益率 ✓
├── fx/currency-cross/            # 货币对
├── credit/spreads/               # 信用利差
├── commodities/energy-futures/   # 能源期货 ✓
└── cross-asset/                  # 跨资产联动
```

---

**总文档数**: 11个
**总Prompts数**: 26个 (5主模板 + 14 Mini + 7 Theme)
**总案例数**: 7个 (2真实 + 5虚构)

**版本**: v0.5
**更新**: 2026-04-29