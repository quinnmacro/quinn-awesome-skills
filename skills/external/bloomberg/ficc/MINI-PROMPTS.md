# FICC Mini Prompts

> 针对特定场景的快速分析 prompts

---

## 一、Daily Workflow Prompts

### 1.1 Pre-Market Scan (早盘扫描)

```
GOAL: Quick FICC market scan before trading session.

OUTPUT FORMAT:

**Rates Snapshot**
| Market | 10Y Yield | MTD Move | Key Driver |
|--------|-----------|----------|------------|
| US | [value] | [bp] | [policy/data] |
| EUR | [value] | [bp] | [policy/data] |
| UK | [value] | [bp] | [policy/data] |

**Credit Quick Check**
| Index | OAS | MTD Chg | Risk Signal |
|-------|-----|---------|-------------|
| US IG | [bp] | [bp] | [tightening/widening] |
| US HY | [bp] | [bp] | [tightening/widening] |

**FX Mood**
| Pair | Spot | MTD Move | Carry |
|------|------|----------|-------|
| EUR/USD | [value] | [%] | [sign] |
| USD/JPY | [value] | [%] | [sign] |

**Commodities**
| Commodity | Front Month | MTD Move | Curve Shape |
|-----------|-------------|----------|-------------|
| WTI | [$] | [%] | [contango/back] |
| Brent | [$] | [%] | [contango/back] |

**Risk Appetite**
- VIX: [value] — [calm/elevated/stressed]
- OVX: [value] — [calm/elevated/stressed]
- Risk Regime: [risk-on/risk-off/mixed]

SOURCE: Bloomberg real-time data
```

### 1.2 Close Review (收盘复盘)

```
GOAL: End-of-day FICC market review with key moves and drivers.

OUTPUT FORMAT:

**Top 3 Moves Today**

1. [Asset]: [change] — [driver]
2. [Asset]: [change] — [driver]
3. [Asset]: [change] — [driver]

**Rates Session Summary**
| Market | Open | Close | Session Move | Driver |
|--------|------|-------|--------------|--------|
| US 10Y | [value] | [value] | [bp] | [data/flow] |
| EUR 10Y | [value] | [value] | [bp] | [data/flow] |

**Credit Flow Check**
| Metric | Value | Interpretation |
|--------|-------|----------------|
| IG Spread Change | [bp] | [tightening/widening] |
| HY Spread Change | [bp] | [tightening/widening] |
| New Issue Today | [$bn] | [heavy/light] |
| CDS-Bond Basis | [bp] | [CDS rich/bond rich] |

**FX Session Recap**
| Pair | High | Low | Close | Intraday Range |
|------|------|-----|-------|----------------|
| EUR/USD | [value] | [value] | [value] | [pips] |
| USD/JPY | [value] | [value] | [value] | [pips] |

**Tomorrow's Focus**
- Key data: [list scheduled releases]
- Central bank: [any meetings/comments]
- Risk events: [geopolitical/supply]

SOURCE: Bloomberg intraday data + news flow
```

### 1.3 Weekly Wrap (周度总结)

```
GOAL: Weekly FICC performance summary and trend assessment.

OUTPUT FORMAT:

**Week Performance Summary**

| Asset Class | Week Chg | YTD Chg | Trend |
|-------------|----------|---------|-------|
| US 10Y | [bp] | [bp] | [↑/↓/flat] |
| EUR 10Y | [bp] | [bp] | [↑/↓/flat] |
| USD Index | [%] | [%] | [↑/↓/flat] |
| US IG OAS | [bp] | [bp] | [↑/↓/flat] |
| WTI | [%] | [%] | [↑/↓/flat] |

**Curve Evolution**
| Market | 2Y-10Y Slope | Week Ago | Change | Signal |
|--------|--------------|----------|--------|--------|
| US | [bp] | [bp] | [bp] | [steepening/flattening] |
| EUR | [bp] | [bp] | [bp] | [steepening/flattening] |

**Credit Quality Trend**
| Metric | Current | Week Ago | Change |
|--------|---------|----------|--------|
| IG-HY Ratio | [ratio] | [ratio] | [↑/↓] |
| Upgrades | [count] | - | - |
| Downgrades | [count] | - | - |

**Key Week Drivers**
1. [Event/Data] → [Asset Impact]
2. [Event/Data] → [Asset Impact]
3. [Event/Data] → [Asset Impact]

**Next Week Watch List**
- Scheduled: [data, meetings, events]
- Positioning: [what to watch]
- Breakout levels: [key technicals]

SOURCE: Bloomberg week data + news archive
```

---

## 二、Event-Driven Prompts

### 2.1 Rate Decision Reaction (央行决议反应)

```
GOAL: Immediate analysis after {Central Bank} rate decision.

CONTEXT:
- Decision: [hike/cut/hold]
- Magnitude: [bp change if applicable]
- Statement key points: [extract from news]

OUTPUT FORMAT:

**Decision Summary**
| Element | Value | Market Expectation | Surprise |
|---------|-------|--------------------| ---------|
| Rate Change | [bp] | [expected bp] | [surprise bp] |
| Statement Tone | [hawkish/dovish] | [expected tone] | [surprise direction] |
| Forward Guidance | [text] | [expected text] | [change] |

**Immediate Market Reaction**

| Asset | Pre-Decision | Post-Decision | Move | Speed |
|-------|--------------|---------------|------|-------|
| {Currency} | [value] | [value] | [%] | [minutes] |
| {Bond 10Y} | [yield] | [yield] | [bp] | [minutes] |
| Credit | [OAS] | [OAS] | [bp] | [minutes] |

**Implication Analysis**

1. Policy path repricing: [what changed in forward expectations]
2. Curve impact: [front-end vs long-end move]
3. Cross-asset: [FX, credit, equity linkage]
4. Next meeting: [what's now priced]

**Trading Implications**
- Duration: [bullish/bearish for bonds]
- Curve: [steepener/flattener bias]
- FX: [currency direction]
- Credit: [spread direction]

SOURCE: Bloomberg real-time + news wire
```

### 2.2 Geopolitical Shock (地缘政治冲击)

```
GOAL: Cross-asset reaction analysis for {Geopolitical Event}.

EVENT: {Event Description}
TIMING: {Event Time}

OUTPUT FORMAT:

**Immediate Risk Assets Reaction**

| Asset | Pre-Event | Current | Move | Severity |
|-------|-----------|---------|------|----------|
| VIX | [value] | [value] | [points] | [low/medium/high] |
| OVX | [value] | [value] | [points] | [low/medium/high] |
| USD Index | [value] | [value] | [%] | [safe-haven/risk-off] |
| Gold | [$] | [$] | [%] | [safe-haven demand] |

**Commodity Impact (if supply-related)**
| Commodity | Pre-Event | Current | Move | Curve Impact |
|-----------|-----------|---------|------|--------------|
| WTI | [$] | [$] | [%] | [contango/back change] |
| Brent | [$] | [$] | [%] | [contango/back change] |

**Flight-to-Quality**
| Safe Asset | Pre-Event | Current | Move |
|------------|-----------|---------|------|
| US 10Y | [yield] | [yield] | [bp] |
| German 10Y | [yield] | [yield] | [bp] |
| JPY | [rate] | [rate] | [%] |

**Risk Assessment**
- Supply disruption scale: [estimate]
- Duration uncertainty: [hours/days/weeks]
- Demand destruction risk: [assessment]
- Financial contagion risk: [assessment]

**Historical Comparison**
- Similar event: [past example]
- Past market reaction: [summary]
- Recovery timeline: [past experience]

SOURCE: Bloomberg real-time + news + historical data
```

### 2.3 Data Release Reaction (数据发布反应)

```
GOAL: Market reaction to {Data Release} relative to expectations.

DATA: {Data Name}
RELEASE TIME: {Time}
ACTUAL: [value] | EXPECTED: [value] | SURPRISE: [+/- difference]

OUTPUT FORMAT:

**Surprise Assessment**
| Metric | Actual | Expected | Surprise | Direction |
|--------|--------|----------|----------|-----------|
| {Data Name} | [value] | [value] | [diff] | [beat/miss] |

**Immediate Market Reaction**

| Asset | Pre-Release | Post-Release | Move | Reaction Speed |
|-------|-------------|---------------|------|----------------|
| {Currency} | [value] | [value] | [%] | [seconds/minutes] |
| {Bond 10Y} | [yield] | [yield] | [bp] | [seconds/minutes] |
| Credit | [OAS] | [OAS] | [bp] | [minutes] |

**Policy Implication**
- Rate path repricing: [hike/cut probability change]
- Forward curve shift: [which tenor moved most]
- Central bank guidance read: [alignment with statement]

**Secondary Effects**
- Equity: [index reaction]
- Credit: [IG vs HY divergence]
- Curve: [steepening/flattening from data]

**Historical Pattern**
- Last 5 releases: [summary of surprise patterns]
- Market sensitivity: [how much move per surprise unit]
- Fade tendency: [does reaction persist or reverse]

SOURCE: Bloomberg ECO + real-time market data
```

---

## 三、Relative Value Prompts

### 3.1 Curve Trade Setup (曲线交易设置)

```
GOAL: Identify curve trade opportunity for {Country} yields.

OUTPUT FORMAT:

**Current Curve Shape**
| Spread | Current (bp) | 1W Ago | 1M Ago | Historical Avg |
|--------|--------------|--------|--------|----------------|
| 2Y-10Y | [value] | [value] | [value] | [avg] |
| 5Y-30Y | [value] | [value] | [value] | [avg] |
| 2Y-5Y | [value] | [value] | [value] | [avg] |

**Relative Position vs History**
| Spread | Current vs Avg | Z-Score | Signal |
|--------|----------------|---------|--------|
| 2Y-10Y | [+/- bp] | [value] | [steep/flat/neutral] |
| 5Y-30Y | [+/- bp] | [value] | [steep/flat/neutral] |

**Trade Recommendation**
- Position: [steepener/flattener/neutral]
- Entry level: [current spread]
- Target: [expected spread]
- Stop: [risk level]
- Conviction: [high/medium/low]

**Drivers**
- Policy expectation: [front-end driver]
- Term premium: [long-end driver]
- Supply/demand: [technical factor]

**Risk Factors**
- Data surprises: [what could flip]
- Central bank: [what could surprise]
- Positioning: [crowded trade risk]

SOURCE: Bloomberg yield data + historical analysis
```

### 3.2 Credit Relative Value (信用相对价值)

```
GOAL: Credit relative value opportunity between IG and HY.

OUTPUT FORMAT:

**IG-HY Ratio Analysis**
| Metric | Current | Historical Avg | Current vs Avg |
|--------|---------|----------------|----------------|
| IG OAS | [bp] | [avg bp] | [+/- bp] |
| HY OAS | [bp] | [avg bp] | [+/- bp] |
| IG-HY Ratio | [ratio] | [avg ratio 3-4x] | [above/below avg] |

**Sector Relative Value**
| Sector | IG OAS | HY OAS | Rich/Cheap vs Index |
|--------|--------|--------|---------------------|
| Financials | [bp] | [bp] | [assessment] |
| Energy | [bp] | [bp] | [assessment] |
| Consumer | [bp] | [bp] | [assessment] |
| Tech | [bp] | [bp] | [assessment] |

**Trade Opportunity**
| Setup | Direction | Entry | Target | Conviction |
|-------|-----------|-------|--------|------------|
| IG vs HY | [long IG/short HY] | [ratio] | [ratio] | [level] |
| Sector X vs Sector Y | [long X/short Y] | [spread diff] | [spread diff] | [level] |

**Risk Considerations**
- Default cycle timing
- Liquidity differential
- New issue supply

SOURCE: Bloomberg credit indices + sector data
```

### 3.3 FX Carry Trade (FX Carry 交易)

```
GOAL: FX carry trade attractiveness assessment for {Pair}.

OUTPUT FORMAT:

**Carry Calculation**
| Metric | Value | Source |
|--------|-------|--------|
| Spot | [value] | Current |
| 12M Forward | [value] | Forward market |
| Forward Points | [pips] | Spot - Forward |
| Annual Carry % | [%] | Forward / Spot |
| Rate Differential | [bp] | 10Y bond yields |

**Risk-Adjusted Carry**
| Metric | Value | Interpretation |
|--------|-------|----------------|
| 3M Realized Vol | [%] | Historical volatility |
| Carry-to-Vol Ratio | [ratio] | Sharpe-like metric |
| Break-even Spot Move | [%] | How much FX can move before carry lost |

**Volatility Assessment**
| Metric | Value | Signal |
|--------|-------|--------|
| 3M Implied Vol | [%] | Option market pricing |
| Vol Risk Premium | [bp] | Implied - Realized |
| 25D Risk Reversal | [bp] | Directional skew |

**Trade Recommendation**
- Direction: [long/short base currency]
- Entry: [spot level]
- Carry: [annual %]
- Break-even: [max adverse move]
- Conviction: [high/medium/low]

**Risk Factors**
- Central bank divergence change
- Risk-off event probability
- Positioning crowdedness

SOURCE: Bloomberg FX forwards + vol data
```

---

## 四、Risk & Stress Prompts

### 4.1 Market Stress Check (市场压力检查)

```
GOAL: Quick assessment of current market stress levels across FICC assets.

OUTPUT FORMAT:

**Stress Indicators Dashboard**

| Indicator | Current | Normal Range | Stress Level | Signal |
|-----------|---------|--------------|--------------|--------|
| VIX | [value] | 12-20 | [calm/medium/high] | [color] |
| OVX | [value] | 25-35 | [calm/medium/high] | [color] |
| IG-HY Ratio | [ratio] | 3-4x | [normal/stressed] | [color] |
| 2Y-10Y Slope | [bp] | 50-150 | [normal/flat/inverted] | [color] |
| USD Strength | [index] | 95-105 | [normal/strong] | [color] |

**Stress Regime Classification**
- Overall Stress Level: [Low/Medium/High/Crisis]
- Dominant Stress Source: [rates/credit/geopolitical/liquidity]
- Risk Regime: [risk-on/risk-off/crisis]

**Asset-Specific Stress**

| Market | Stress Metric | Value | Historical %ile |
|--------|---------------|-------|-----------------|
| Rates | Curve volatility | [value] | [%ile] |
| FX | Vol risk premium | [bp] | [%ile] |
| Credit | IG-HY spread diff | [bp] | [%ile] |
| Oil | OVX / spot move | [ratio] | [%ile] |

**Correlation Check**
| Pair | Normal Correlation | Current Correlation | Status |
|------|--------------------|---------------------|--------|
| Rates-FX | 0.3-0.5 | [value] | [aligned/broken] |
| Credit-Equity | 0.3-0.5 | [value] | [aligned/broken] |
| Oil-USD | -0.2 to -0.4 | [value] | [aligned/broken] |

SOURCE: Bloomberg real-time + historical percentile data
```

### 4.2 Liquidity Assessment (流动性评估)

```
GOAL: Assess market liquidity conditions for {Asset Class}.

OUTPUT FORMAT:

**Liquidity Metrics**

| Metric | Current | Historical Avg | Assessment |
|--------|---------|----------------|------------|
| Bid-Ask Spread | [value] | [avg] | [normal/wide] |
| Average Trade Size | [value] | [avg] | [normal/small] |
| Daily Volume | [value] | [avg] | [normal/low] |
| Market Depth | [value] | [avg] | [deep/shallow] |

**Liquidity Stress Signals**

| Signal | Status | Interpretation |
|--------|--------|----------------|
| Spread widening MTD | [+/- bp] | [drying up/normal] |
| Volume decline MTD | [%] | [drying up/normal] |
| Price gaps (intraday) | [count] | [fragmented/smooth] |
| Failed trades/requests | [count] | [stress/normal] |

**Liquidity-by-Tenor (if applicable)**

| Tenor | Bid-Ask | Volume | Liquidity Score |
|-------|---------|--------|-----------------|
| Front-end (2Y) | [spread] | [vol] | [high/medium/low] |
| Belly (5Y-10Y) | [spread] | [vol] | [high/medium/low] |
| Long-end (30Y) | [spread] | [vol] | [high/medium/low] |

**Liquidity Cost Estimate**
- Estimated cost to trade $100mm: [$k]
- Time to execute: [hours/days]
- Market impact: [bp]

**Recommendation**
- Current liquidity: [Excellent/Good/Fair/Poor/Crisis]
- Trading advice: [normal/scale down/wait]

SOURCE: Bloomberg market depth + TRACE (credit) + volume data
```

### 4.3 Position Risk Check (持仓风险检查)

```
GOAL: Assess risk metrics for hypothetical {Position} in {Asset}.

POSITION DETAILS:
- Asset: {Asset/Ticker}
- Direction: [Long/Short]
- Size: [$mm or notional]
- Tenor: [maturity/contract]

OUTPUT FORMAT:

**Market Risk Metrics**

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Current Price/Yield | [value] | Entry reference |
| 1D VaR (95%) | [bp/$] | Expected max 1-day loss |
| 1W VaR (95%) | [bp/$] | Expected max 1-week loss |
| Max adverse move (30D) | [bp/$] | Worst case recently |
| Liquidation cost | [bp/$] | Exit cost estimate |

**Volatility Assessment**

| Metric | Value | Position Impact |
|--------|-------|-----------------|
| 30D Realized Vol | [%] | Historical volatility |
| 3M Implied Vol | [%] | Option market pricing |
| Vol Risk Premium | [bp] | Implied - Realized |
| Tail Risk (1%) | [bp/$] | Extreme scenario |

**Curve/Spread Risk (if applicable)**

| Risk Type | DV01/CS01 | Scenario Impact |
|-----------|-----------|-----------------|
| Parallel shift (+100bp) | [$] | [impact] |
| Curve twist (10bp) | [$] | [impact] |
| Spread widening (+50bp) | [$] | [impact] |

**Correlation Risk**

| Correlated Asset | Correlation | Joint Risk |
|------------------|-------------|------------|
| {Asset 2} | [value] | [correlated move impact] |
| {Asset 3} | [value] | [correlated move impact] |

**Stop-Loss Recommendation**
- Recommended stop level: [price/yield]
- Stop distance: [bp/$]
- Stop probability: [%]

SOURCE: Bloomberg risk analytics + vol data
```

---

## 五、Data & Timing Prompts

### 5.1 Economic Data Calendar (经济数据日历)

```
GOAL: Show upcoming economic data releases relevant to {Market/Theme}.

OUTPUT FORMAT:

**Next 7 Days Data Calendar**

| Date | Release | Market | Importance | Expectation | Potential Impact |
|------|---------|--------|------------|-------------|------------------|
| [date] | [data name] | [market] | [high/medium/low] | [expected value] | [if surprise] |

**Tier-1 Data (High Impact)**

| Data | Last Value | Expectation | Surprise Range | Market Sensitivity |
|------|------------|-------------|----------------|--------------------|
| CPI | [value] | [value] | [+/- range] | [bp per surprise] |
| NFP | [value] | [value] | [+/- range] | [bp per surprise] |
| GDP | [value] | [value] | [+/- range] | [bp per surprise] |

**Market Sensitivity Summary**
- Rates: Most sensitive to [data type], [bp move per unit surprise]
- FX: Most sensitive to [data type], [% move per unit surprise]
- Credit: Secondary sensitivity, follows rates

**Positioning Ahead of Data**
- Current positioning: [from flow data if available]
- Risk: [surprise direction most painful]
- Recommendation: [lighten/hold/add]

SOURCE: Bloomberg ECO calendar + historical sensitivity
```

### 5.2 Central Bank Calendar (央行日历)

```
GOAL: Show upcoming central bank meetings and expected actions.

OUTPUT FORMAT:

**Next 30 Days CB Meetings**

| Date | Central Bank | Current Rate | Expected Action | Market Pricing | Key Focus |
|------|--------------|--------------|-----------------|----------------|-----------|
| [date] | [CB name] | [%] | [hike/cut/hold] | [% change] | [statement focus] |

**Meeting Deep Dive: {Next Major Meeting}**

| Metric | Value |
|--------|-------|
| Current Rate | [%] |
| Market Implied Rate | [%] |
| Expected Change | [bp] |
| Probability Distribution | [cut X% / hold Y% / hike Z%] |
| Key Statement Topics | [list] |

**Forward Path After Meeting**
- Meeting outcome scenarios:
  - Scenario A (expected): [rate path]
  - Scenario B (hawkish surprise): [rate path]
  - Scenario C (dovish surprise): [rate path]

**Cross-CB Comparison**
| CB | Policy Direction | Terminal Rate Estimate | Divergence vs Fed |
|----|-------------------|------------------------|-------------------|
| Fed | [direction] | [%] | [reference] |
| ECB | [direction] | [%] | [converging/diverging] |
| BOJ | [direction] | [%] | [converging/diverging] |

SOURCE: Bloomberg CB calendar + OIS forwards
```

---

## 六、使用场景速查

| 场景 | 用哪个 Prompt | 输入 |
|------|----------------|------|
| **早盘准备** | Pre-Market Scan | 无变量 |
| **日终复盘** | Close Review | 无变量 |
| **周度总结** | Weekly Wrap | 无变量 |
| **央行决议** | Rate Decision Reaction | `{Central Bank}` |
| **地缘冲击** | Geopolitical Shock | `{Event}` |
| **数据发布** | Data Release Reaction | `{Data Name}` |
| **曲线交易** | Curve Trade Setup | `{Country}` |
| **信用RV** | Credit Relative Value | 无变量 |
| **FX Carry** | FX Carry Trade | `{Currency Pair}` |
| **压力检查** | Market Stress Check | 无变量 |
| **流动性** | Liquidity Assessment | `{Asset Class}` |
| **持仓风险** | Position Risk Check | `{Position}`, `{Asset}` |
| **数据日历** | Economic Data Calendar | `{Market}` |
| **央行日历** | Central Bank Calendar | 无变量 |

---

## 七、Prompt 组合使用

### 7.1 早盘完整流程

```
Step 1: Pre-Market Scan → 市场快览
Step 2: Market Stress Check → 压力状态
Step 3: Economic Data Calendar → 当日风险事件
Step 4: Central Bank Calendar → 近期政策风险
Step 5: 决定交易策略
```

### 7.2 事件驱动流程

```
Step 1: Geopolitical Shock / Rate Decision / Data Release → 事件分析
Step 2: Market Stress Check → 市场反应强度
Step 3: cross-asset → 传导路径
Step 4: Close Review → 日终复盘
```

### 7.3 交易想法流程

```
Step 1: Curve Trade Setup / Credit RV / FX Carry → 识别机会
Step 2: Position Risk Check → 评估风险
Step 3: Liquidity Assessment → 评估流动性
Step 4: 执行决策
```

---

**版本**: v0.2
**状态**: Ready for testing
**新增**: Stress + Liquidity + Position Risk + Calendar prompts