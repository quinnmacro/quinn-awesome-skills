# FICC Prompts 设计思路

> Bloomberg AI (ASKB) FICC 专属 prompts 的设计方法论

---

## 一、FICC 的特殊性

### 1.1 与 Equity 的本质区别

| 维度 | Equity | FICC |
|------|--------|------|
| **定价锚点** | 未来现金流折现 | 无风险利率 + 利差 |
| **时间维度** | 长期价值 | 短期-中期，曲线结构 |
| **驱动因素** | 公司基本面 | 宏观 + 央行 + 流动性 |
| **分析框架** | DCF、相对估值 | 曲线分析、利差分解、carry |
| **数据密度** | 季度财报 | 实时 tick 数据，日频更新 |
| **交易视角** | Long/Short | Curve、Spread、Basis、Vol |

**核心差异**：FICC 是 **相对定价** 世界，不是绝对定价。

### 1.2 FICC 四大支柱

| 支柱 | 核心变量 | Bloomberg DAPI 关键字段 |
|------|----------|------------------------|
| **Rates (利率)** | 收益率曲线、央行政策 | `YLD_YTM_MID`, `GOVT_YLD_CURVE`, `FUT_CUR_PRICE` |
| **FX (外汇)** | 货币对、利率差、carry | `CRNCY_CROSS_RATE`, `FORWARD_POINTS`, `FX_OPTION_VOL` |
| **Credit (信用)** | OAS、评级、行业利差 | `OAS_Z_SPREAD`, `CDS_SPREAD`, `RATING_ISSUED` |
| **Commodities (商品)** | 期货曲线、库存、basis | `FUT_CURVE_ACTIVE`, `CRUD_OIL_WTI`, `GOLD_SPOT` |

---

## 二、FICC Prompt 设计原则

### 2.1 必须有的元素

1. **时间优先规则** - FICC 数据时效性强
   - 实时数据 vs 日终数据 vs 周频数据
   - 早盘、盘中、收盘的优先级

2. **曲线思维** - 不是单点，是整条曲线
   - 2Y-5Y-10Y-30Y 的相对位置
   - Contango vs Backwardation
   - Flatteners vs Steepeners

3. **利差分解** - 相对定价的核心
   - Country spread vs Currency spread
   - Rating spread vs Sector spread
   - Term spread vs Credit spread

4. **跨资产联动** - FICC 的 alpha 来源
   - Rates → FX → Credit → Commodities
   - Macro → Micro 的传导路径

### 2.2 数据字段规范

**Bloomberg DAPI 字段命名规则**：
- `_MID` : 中间价
- `_YTM` : 到期收益率
- `_OAS` : Option-Adjusted Spread
- `_BP` : Basis Points (基点)
- `_CURVE` : 曲线数据
- `PX_LAST` : 最新价格
- `CHG_PCT_MTD` : 月度变化百分比
- `CHG_PCT_YTD` : 年度变化百分比

**时间规则**：
- `MTD` : Month-to-Date
- `YTD` : Year-to-Date
- `N` : Period count (N=4 表示过去 4 期)

**Ticker 后缀规则**：
| 类型 | 后缀 | 示例 |
|------|------|------|
| Government Bond | `Govt` | GT10 Govt, GTDEM10Y Govt |
| Index | `Index` | GJGB10 Index, LCGDTRUU Index |
| Commodity Future | `Comdty` | CL1 Comdty, CO1 Comdty |
| Currency | `Curncy` | EURUSD Curncy |
| Corp Bond | `Corp` | 具体ISIN |

### 2.3 数据查询方法优先级

**优先级排序**：

| 方法 | 适用场景 | 优先级 |
|------|----------|--------|
| **BQL** | 批量查询、变化计算、曲线数据 | ★★★★★ |
| **BDP** | 单点数据、当前价格、静态字段 | ★★★★☆ |
| **BDH** | 历史时间序列 | ★★★☆☆ |
| **VCUB** | 期权波动率曲面 | ★★☆☆☆ |

**BQL 示例（推荐用于变化数据）**：
```
for(['GTDEM10Y Govt', 'GTDEM2Y Govt'])
get(pct_chg(yield(dates=MTD)), pct_chg(yield(dates=YTD)), yield)
with(fill=PREV)
```

**BDP 示例（单点查询）**：
```
BDP("CL1 Comdty", "PX_LAST")
BDP("OVX Index", "PX_LAST")
```

### 2.4 FICC 必须包含的风险指标

| 资产类别 | 核心风险指标 | 数据源 |
|----------|--------------|--------|
| Rates | 曲线斜率变化、央行定价偏离 | GT series + OIS forwards |
| FX | Carry、Vol Risk Premium、Risk Reversal | Forward points + VCUB |
| Credit | IG-HY Ratio、Rating Migration、CDS-Bond Basis | Index OAS + Rating actions |
| Commodities | OVX、曲线结构变化、库存偏离 | CL/CO + OVX + EIA |
| Cross-Asset | Risk Regime、Correlation Breakdown | VIX + Spread ratios |

---

## 三、五大模板设计

### 3.1 Sovereign Yields (国债收益率)

**核心问题**：
- 曲线形态的驱动因素？
- 央行政策的市场定价？
- 国际利差和 FX 的联动？

**数据源**：
- 本国国债曲线 (2Y-5Y-10Y-30Y)
- 对比国曲线 (如 USD vs EUR vs JPY)
- 央行政策利率预期

**输出结构**：
1. 曲线快照 (当日形态)
2. 曲线变化 (MTD/YTD shifts)
3. 央行定价 (rate path implied)
4. 跨国利差 (vs 主要对手)
5. FX 联动 (利差驱动的货币走势)

### 3.2 Currency Cross (货币对)

**核心问题**：
- 利率差的 carry 价值？
- 央行分歧的定价？
- 技术位置和支撑阻力？

**数据源**：
- Spot rate
- Forward points (1M-3M-6M-12M)
- Rate differential (implied)
- Option vol (risk reversal)

**输出结构**：
1. 即期快照
2. Forward 结构 (carry 分析)
3. 央行分歧 (两国 policy divergence)
4. 技术分析 (关键位置)
5. 风险指标 (vol, risk reversal)

### 3.3 Credit Spreads (信用利差)

**核心问题**：
- IG vs HY 的相对价值？
- 行业利差的轮动？
- 评级迁徙信号？

**数据源**：
- Index OAS (IG: LCGDTRUU, HY: HLHO)
- Single name CDS
- Rating actions
- New issue pipeline

**输出结构**：
1. Index level 快照
2. IG vs HY spread ratio
3. 行业利差矩阵
4. 评级迁徙统计
5. 新发行动态

### 3.4 Energy Futures (能源期货)

**核心问题**：
- 曲线结构的含义？
- 库存和 fundamentals？
- Time spread 的交易机会？

**数据源**：
- WTI/Brent futures curve
- Time spreads (M1-M2, M2-M3)
- Inventory data (EIA)
- Crack spreads

**输出结构**：
1. Spot 和 front month
2. 曲线形态 (contango/backwardation)
3. Time spreads 变化
4. 库存和 fundamentals
5. 相关产品 (crack, gasoil)

### 3.5 Cross-Asset (跨资产联动)

**核心问题**：
- 当前的主导叙事？
- 资产间的传导路径？
- 破裂信号在哪里？

**数据源**：
- 所有四大支柱的核心指标
- Macro surprise index
- Risk appetite indicators

**输出结构**：
1. Macro backdrop
2. Rates → FX 传导
3. FX → Credit 传导
4. Credit → Commodities 传导
5. Risk appetite 综合

---

## 四、迭代方法论

### 4.1 测试流程

```
1. 写 prompt → Bloomberg {AKSB <GO>}
2. 观察输出 → 识别问题
3. 分类问题：
   - 数据字段错误 → 检查 DAPI
   - 数据缺失/显示N/A → 强化查询方法和ticker明确性
   - 结构混乱 → 重写 ANALYSIS FRAMEWORK
   - 变量缺失 → 补充 USER INPUTS
   - 输出格式差 → 优化 TABLE STANDARDS
   - 图表/分析太简单 → 添加波动率等风险指标
4. 修正 → 再测试
```

### 4.2 常见问题预案

| 问题类型 | 解决方案 |
|----------|----------|
| 字段不返回 | 换字段名，或加 fallback |
| 显示 N/A | 明确ticker格式 + 查询方法优先级 |
| 曲线数据不全 | 明确 curve points (2Y-5Y-10Y-30Y) |
| 时间范围混乱 | 明确 MTD/YTD/N+1 规则 |
| 跨资产缺失 | 补充具体 ticker 列表 |
| 分析太浅 | 添加波动率、风险指标、分解分析 |

### 4.3 测试反馈汇总（v0.1-v0.2）

| 模板 | 问题 | 解决方案 | 状态 |
|------|------|----------|------|
| sovereign-yields v0.1 | EUR MTD/YTD 显示"—" | 添加BQL查询方法示例，明确pct_chg用法 | ✓ 修复 |
| sovereign-yields v0.1 | EUR-JPY spread 显示N/A | 明确对比ticker，添加Govt/Index后缀说明 | ✓ 优化 |
| energy-futures v0.1 | 图表太简单，缺少波动率 | 添加VOLATILITY ANALYSIS部分，OVX指标 | ✓ 增强 |

---

## 五、Bloomberg 约定

### 5.1 核心指数 Ticker

| 类型 | Ticker | 说明 |
|------|--------|------|
| US IG Credit | `LCGDTRUU` | Bloomberg USD IG Index |
| US HY Credit | `HLHO` | Bloomberg USD HY Index |
| US Treasury | `USGG10YR` | 10Y US Treasury Yield |
| EUR Rates | `GDBR10` | German 10Y Bund |
| JPY Rates | `GJGB10` | Japan 10Y JGB |
| WTI Crude | `CL1` | WTI Front Month |
| Brent Crude | `CO1` | Brent Front Month |

### 5.2 字段速查

```
# Yields
YLD_YTM_MID          # Yield to maturity
GOVT_YLD_CURVE       # Government yield curve

# Credit
OAS_Z_SPREAD         # Option-adjusted spread
CDS_SPREAD_5Y        # 5Y CDS spread

# FX
CRNCY_CROSS_RATE     # Currency cross rate
FX_FWD_POINTS        # Forward points

# Commodities
FUT_CURVE_ACTIVE     # Active futures curve
```

---

## 六、实战案例分析

### 6.1 案例记录格式

每次测试或实际使用后，记录案例以便迭代：

```markdown
## 案例：{Date} - {Template} - {Input}

### 输入变量
- {Variable 1}: [value]

### 输出质量评估

| 维度 | 评分 (1-5) | 问题 |
|------|------------|------|
| 数据完整性 | [score] | [missing data?] |
| 结构清晰度 | [score] | [sections clear?] |
| 分析深度 | [score] | [insightful?] |
| 可操作性 | [score] | [actionable?] |

### 具体问题
1. [问题描述]

### 解决方案
1. [修改建议]

### 版本更新
- Before: v0.x → After: v0.x+1
```

### 6.2 测试案例库

| Date | Template | Input | Status | Key Finding |
|------|----------|-------|--------|-------------|
| 2026-04-28 | sovereign-yields | EUR | ✓ | MTD/YTD need BQL method |
| 2026-04-28 | energy-futures | WTI | ✓ | Need volatility section |
| - | currency-cross | - | Pending | - |
| - | spreads | - | Pending | - |
| - | cross-asset | - | Pending | - |

---

## 七、FICC 交易策略框架

### 7.1 Rates 策略类型

| 策略 | 描述 | Prompt 支持 |
|------|------|-------------|
| **Directional** | Long/Short specific maturity | sovereign-yields |
| **Curve** | Steepener/Flattener | Mini: Curve Trade Setup |
| **Cross-Market** | US-EUR, US-JPY spread | sovereign-yields |
| **Carry & Roll** | Harvest roll yield | sovereign-yields |

### 7.2 FX 策略类型

| 策略 | 描述 | Prompt 支持 |
|------|------|-------------|
| **Directional** | Long/Short currency | currency-cross |
| **Carry** | High-yield vs low-yield | currency-cross + Mini: FX Carry |
| **Vol** | Long/Short vol via options | currency-cross (vol metrics) |
| **Event** | Data/CB positioning | Mini: Rate Decision Reaction |

### 7.3 Credit 策略类型

| 策略 | 描述 | Prompt 支持 |
|------|------|-------------|
| **Directional** | Long/Short credit | spreads |
| **IG-HY Switch** | Rotate IG/HY | spreads + Mini: Credit RV |
| **Sector Rotation** | Sector relative value | spreads |
| **New Issue** | Primary market arb | spreads |

### 7.4 Commodities 策略类型

| 策略 | 描述 | Prompt 支持 |
|------|------|-------------|
| **Directional** | Long/Short commodity | energy-futures |
| **Curve** | Calendar spreads | energy-futures |
| **Vol** | Options strategies | energy-futures (vol section) |
| **Crack** | Refinery margin trade | energy-futures |

---

## 八、风险场景分析

### 8.1 市场压力指标

| 指标 | 正常范围 | 压力阈值 | 数据源 |
|------|----------|----------|--------|
| VIX | 12-20 | >30 | VIX Index |
| OVX | 25-35 | >50 | OVX Index |
| IG-HY Ratio | 3-4x | >5x | LCGDTRUU, HLHO |
| 2Y-10Y Slope | 50-150bp | <50 (flat) | GT series |

### 8.2 压力传导路径

```
Trigger → First Asset → Second Asset → Final Impact

Example:
Rate Shock (+100bp Fed)
→ US 10Y +50bp
→ USD +2%
→ EM credit +100bp
```

---

## 九、数据源详解

### 9.1 Bloomberg 数据层级

| 层级 | 类型 | 示例 |
|------|------|------|
| **Real-time** | Live quotes | PX_LAST, PX_BID |
| **Daily** | Close prices | PX_CLOSE_1D |
| **Historical** | Time series | BDH function |
| **Fundamental** | Economic data | ECO function |
| **Derived** | Calculations | BQL |

### 9.2 外部数据源

| 来源 | 数据类型 | Bloomberg 函数 |
|------|----------|----------------|
| **EIA** | Energy inventory | DOEWCADS Index |
| **OPEC** | Production | OPEC news |
| **Rating Agencies** | Rating actions | NEWS |

---

## 十、模板使用指南

### 10.1 模板选择决策树

```
问题是什么？
│
├─ 国债收益率？→ sovereign-yields / Mini: Quick Yield
├─ 货币对？→ currency-cross / Mini: FX Carry
├─ 信用市场？→ spreads / Mini: Quick Credit
├─ 商品期货？→ energy-futures / Mini: Quick Curve
├─ 跨资产？→ cross-asset / Mini: Pre-Market Scan
├─ 突发事件？→ Mini: Rate Decision / Geopolitical / Data Release
├─ 日终复盘？→ Mini: Close Review
├─ 周度总结？→ Mini: Weekly Wrap
└─ 交易机会？→ Mini: Curve Trade / Credit RV / FX Carry
```

### 10.2 变量填写指南

| 模板 | 变量 | 可选值 |
|------|------|--------|
| sovereign-yields | Country/Currency | US, EUR, JPY, UK, AU, CN |
| currency-cross | Currency Pair | EURUSD, USDJPY, GBPUSD |
| spreads | Market/Region | US, EUR, UK, Asia USD |
| energy-futures | Commodity | WTI, Brent, Natural Gas |
| cross-asset | Theme | Iran War, Fed Pause, China Recovery |

---

## 十一、下一步

1. 继续测试 currency-cross, spreads, cross-asset
2. 根据反馈迭代模板
3. 添加更多 Mini Prompts（压力测试、流动性分析）
4. 建立案例库

---

**版本**: v0.4
**状态**: Active Development
**最后更新**: 2026-04-28