# FICC 专题分析 Prompts

> 基于宏观主题的深度分析场景

---

## 一、宏观交易主题

### 1.1 Inflation Trade Analysis (通胀交易)

```
GOAL: Comprehensive inflation trade analysis - positioning for higher/lower inflation regime.

USER INPUT:
- Direction: [Long Inflation / Short Inflation]
- Focus Market: [US / EUR / Global]
- Time Horizon: [Near-term / Medium-term / Long-term]

OUTPUT FORMAT:

**Inflation Dashboard**

| Metric | Current | Trend | Market Pricing |
|--------|---------|-------|----------------|
| Headline CPI | [%] | [↑/↓] | [vs expectations] |
| Core CPI | [%] | [↑/↓] | [vs expectations] |
| PCE (if US) | [%] | [↑/↓] | [Fed target reference] |
| Inflation Expectations (5Y) | [%] | [↑/↓] | [breakeven level] |
| Wage Growth | [%] | [↑/↓] | [labor cost pressure] |

**Inflation Breakeven Analysis**

| Breakeven | Current | 1Y Ago | Interpretation |
|-----------|---------|--------|----------------|
| 5Y Breakeven | [bp] | [bp] | [inflation premium priced] |
| 10Y Breakeven | [bp] | [bp] | [long-term inflation view] |
| 5Y5Y Forward | [bp] | [bp] | [inflation persistence] |

**Inflation Trade Positions**

| Position | Long Inflation | Short Inflation | Data Required |
|----------|----------------|-----------------|---------------|
| Rates | Short duration | Long duration | Curve, DV01 |
| Curve | Steepener | Flattener | 2Y-10Y spread |
| TIPS | Long TIPS | Short TIPS | Breakeven spread |
| Commodities | Long energy | Short energy | Oil curve |
| FX | Short JPY/CHF | Long JPY/CHF | Funding currencies |
| Credit | Short HY | Long IG | IG-HY ratio |

**Inflation Sensitivity Matrix**

| Asset | Inflation +1% Move | Mechanism |
|-------|--------------------|-----------|
| 10Y Nominal | [+/- bp] | Real yield + inflation premium |
| 5Y Breakeven | [+/- bp] | Direct inflation pricing |
| WTI | [+/- %] | Demand + supply cost |
| USD | [+/- %] | Fed reaction + real rates |
| Gold | [+/- %] | Inflation hedge demand |
| IG Credit | [+/- bp] | Rate pass-through |

**Central Bank Reaction Function**

| Inflation Outcome | CB Response Probability | Market Implication |
|-------------------|-------------------------|--------------------|
| CPI > 3% | [rate path] | [curves/spreads move] |
| CPI 2-3% | [rate path] | [curves/spreads move] |
| CPI < 2% | [rate path] | [curves/spreads move] |

**Trade Recommendation**

Entry Conditions:
- [Trigger 1]: Inflation surprise direction
- [Trigger 2]: CB response signal
- [Trigger 3]: Breakeven move confirmation

Position Structure:
- Primary: [main position]
- Hedge: [risk mitigation]
- Conviction: [1-5 score]

SOURCE: Bloomberg inflation data + breakevens + CB calendar
```

---

### 1.2 Recession Trade Analysis (衰退交易)

```
GOAL: Recession trade positioning - prepare for economic downturn scenario.

USER INPUT:
- Probability Assessment: [High / Medium / Low recession risk]
- Timing: [imminent / 6-12 months / 12+ months]
- Severity: [mild / moderate / severe]

OUTPUT FORMAT:

**Recession Indicator Dashboard**

| Indicator | Current | Recession Signal | Historical Accuracy |
|-----------|---------|------------------|---------------------|
| Yield Curve (2Y-10Y) | [bp] | [inverted?] | [historical track record] |
| Unemployment Rate | [%] | [rising?] | [Sahm Rule check] |
| ISM Manufacturing | [value] | [<50?] | [contraction?] |
| Consumer Confidence | [value] | [declining?] | [sentiment signal] |
| Leading Economic Index | [value] | [trend] | [composite signal] |

**Recession Probability Assessment**

| Model/Signal | Probability | Weight | Contribution |
|--------------|-------------|--------|--------------|
| Curve inversion | [%] | [weight] | [combined] |
| Sahm Rule | [%] | [weight] | [combined] |
| LEI decline | [%] | [weight] | [combined] |
| Credit spreads | [%] | [weight] | [combined] |
| **Composite** | [%] | - | Final assessment |

**Recession Trade Positions**

| Asset | Mild Recession | Moderate Recession | Severe Recession |
|-------|----------------|--------------------|--------------------|
| Duration | +20bp 10Y | +50bp 10Y | +100bp 10Y |
| Curve | Flattener | Bull flattener | Extreme flattening |
| Credit | IG flat, HY +50bp | IG +20bp, HY +100bp | IG +50bp, HY +200bp |
| FX | JPY +2% | JPY +5% | JPY +10% |
| Equities | -10% | -20% | -30% |
| Commodities | -5% | -15% | -30% |

**Recession Timeline Impact**

| Phase | Duration | Credit | FX | Commodities |
|-------|----------|--------|----| -------------|
| Pre-recession (now) | [months] | [spread level] | [rate] | [price] |
| Recession onset | [months] | [spread peak] | [rate peak] | [price trough] |
| Recession trough | [months] | [spread compression] | [rate] | [recovery?] |
| Recovery | [months] | [normalizing] | [normalizing] | [recovery] |

**Policy Response Expectation**

| Severity | Fed Response | ECB Response | Fiscal Response |
|----------|--------------|--------------|-----------------|
| Mild | -50bp | -25bp | Limited |
| Moderate | -100bp | -50bp | Moderate stimulus |
| Severe | -200bp+ | -100bp+ | Major stimulus |

**Trade Recommendation**

Positioning:
- Duration: [direction] based on severity assessment
- Curve: [flattener/steepener] based on policy response
- Credit: [IG vs HY] based on risk appetite
- FX: [funding currencies] safe-haven demand
- Commodities: [demand destruction] exposure

Risk Factors:
- Recession avoids: Position unwinds quickly
- Policy aggressive: Limits duration gains
- Inflation persists: Fed can't cut as much

SOURCE: Bloomberg recession indicators + historical analogs
```

---

### 1.3 Liquidity Crisis Analysis (流动性危机)

```
GOAL: Liquidity crisis detection and positioning - market functioning stress.

USER INPUT:
- Severity: [Emerging / Moderate / Severe / Crisis]
- Asset Focus: [Rates / Credit / FX / All markets]

OUTPUT FORMAT:

**Liquidity Stress Indicators**

| Indicator | Current | Normal | Stress Level | Signal |
|-----------|---------|--------|--------------|--------|
| Bid-Ask Spread (US 10Y) | [bp] | [0.5bp] | [score] | [normal/wide] |
| Bid-Ask Spread (IG Index) | [bp] | [1bp] | [score] | [normal/wide] |
| FX Spot Spreads | [pips] | [0.5] | [score] | [normal/wide] |
| Treasury Market Depth | [$bn] | [normal] | [score] | [deep/shallow] |
| Repo Rate Spread | [bp] | [normal] | [score] | [normal/stressed] |

**Market Functioning Check**

| Market | Functioning Score | Evidence |
|--------|-------------------|----------|
| Treasury | [score] | [spread, depth, turnover] |
| Credit | [score] | [TRACE volume, dealer inventory] |
| FX | [score] | [turnover, forward spreads] |
| Futures | [score] | [open interest, volume] |

**Liquidity Transmission**

| Stress Origin | First Impact | Second Impact | Final Impact |
|---------------|--------------|---------------|--------------|
| [source] | [asset 1] | [asset 2] | [asset 3] |

**Historical Liquidity Crisis Comparison**

| Crisis | Year | Peak Stress | Duration | Recovery |
|--------|------|-------------|----------|----------|
| COVID | 2020 | [metrics] | [weeks] | [timeline] |
| GFC | 2008 | [metrics] | [months] | [timeline] |
| 2019 Repo | 2019 | [metrics] | [days] | [timeline] |

**Liquidity Crisis Trades**

| Position | Crisis Play | Recovery Play | Risk |
|----------|-------------|---------------|------|
| Rates | Front-end rich (cash hoarding) | Curve normalize | Policy intervention |
| Credit | IG better than HY | HY recovers faster | Default cascade |
| FX | Funding currencies bid | Carry currencies bid | Central bank swap lines |
| Vol | Long vol everywhere | Short vol | Vol crush on intervention |

**Central Bank Intervention Expectation**

| Tool | Probability | Impact |
|------|-------------|--------|
| Rate cut | [%] | [effect] |
| QE restart | [%] | [effect] |
| Swap lines | [%] | [effect] |
| Repo operations | [%] | [effect] |
| Direct market support | [%] | [effect] |

**Trade Recommendation**

Current Assessment:
- Liquidity Score: [1-10]
- Trend: [improving / stable / deteriorating]
- Intervention Likelihood: [%]

Positioning:
- If Crisis: [flight to quality positions]
- If Recovery: [normalization positions]
- If Intervention: [policy-sensitive positions]

SOURCE: Bloomberg liquidity metrics + dealer data + central bank operations
```

---

## 二、央行博弈场景

### 2.1 Central Bank Divergence Trade (央行分歧交易)

```
GOAL: Trade the divergence between central bank policies.

USER INPUT:
- Primary CB: [Fed / ECB / BOJ / BOE]
- Secondary CB: [Fed / ECB / BOJ / BOE]
- Trade Direction: [Long divergence / Short divergence]

OUTPUT FORMAT:

**Policy Divergence Dashboard**

| Central Bank | Current Rate | Next Move Expected | Timing | Bias |
|--------------|--------------|--------------------|--------|------|
| {Primary CB} | [%] | [+/- bp] | [meeting date] | [hawkish/dovish] |
| {Secondary CB} | [%] | [+/- bp] | [meeting date] | [hawkish/dovish] |

**Divergence Metrics**

| Metric | Current | 1Y Expected | Trend |
|--------|---------|-------------|-------|
| Rate Differential | [bp] | [bp] | [widening/narrowing] |
| Policy Bias Differential | [score] | - | [ hawkish gap] |
| Meeting Timing Gap | [days] | - | [who moves first] |
| Market Pricing Gap | [bp] | - | [surprise risk] |

**Divergence Trade Positions**

| Trade | Long Divergence | Short Divergence | Mechanism |
|-------|-----------------|------------------|-----------|
| Rates Cross | Short {Primary} bond, Long {Secondary} bond | Reverse | Rate path pricing |
| FX | Long {Primary} currency | Long {Secondary} currency | Carry + policy |
| Curve | {Primary} flattener, {Secondary} steepener | Reverse | Policy speed diff |
| Credit | {Primary} region credit short | {Primary} region credit long | Rate pass-through |

**Meeting Scenario Analysis**

| Scenario | Primary Outcome | Secondary Outcome | Trade Impact |
|----------|-----------------|-------------------|--------------|
| A (Expected) | [action] | [action] | [price move] |
| B (Primary surprise) | [surprise] | [expected] | [price move] |
| C (Secondary surprise) | [expected] | [surprise] | [price move] |
| D (Both surprise) | [surprise] | [surprise] | [price move] |

**Historical Divergence Episodes**

| Episode | Year | Divergence | Trade Result |
|---------|------|------------|--------------|
| Fed vs ECB 2014-2016 | 2014 | Fed hawkish, ECB dovish | EUR/USD -25% |
| BOJ vs Fed 2013 | 2013 | BOJ easing, Fed taper | USD/JPY +20% |
| Fed vs ECB 2022 | 2022 | Both hawkish (convergence) | EUR/USD stabilized |

**Trade Recommendation**

Entry Conditions:
- Divergence confirmed: [rate differential widening X bp]
- Market pricing: [gap vs official guidance Y bp]
- Catalyst: [upcoming meeting/data]

Position Structure:
- Primary: [main divergence trade]
- Hedge: [convergence risk protection]
- Conviction: [score]

Timing:
- Entry: [before/after meeting]
- Duration: [expected hold period]
- Exit triggers: [convergence signals]

SOURCE: Bloomberg CB calendar + OIS forwards + rate pricing
```

---

### 2.2 Policy Mistake Trade (政策失误交易)

```
GOAL: Position for central bank policy mistake scenario.

USER INPUT:
- Central Bank: [Fed / ECB / BOJ / BOE]
- Mistake Type: [Over-tightening / Under-tightening / Wrong timing]
- Market Impact: [Duration / Credit / FX / All]

OUTPUT FORMAT:

**Policy Mistake Definition**

| Mistake Type | Definition | Historical Examples |
|--------------|------------|---------------------|
| Over-tightening | Rates too high vs economy needs | Fed 2000, ECB 2011 |
| Under-tightening | Rates too low vs inflation risk | Fed 2021-2022 delay |
| Wrong timing | Move too early/late | BOJ premature exit attempts |

**Policy Mistake Signals**

| Signal | Current Value | Mistake Threshold | Probability |
|--------|---------------|-------------------|-------------|
| Real rates | [value] | [too negative/positive] | [%] |
| Rate vs neutral | [bp] | [gap to estimated neutral] | [%] |
| Forward guidance vs data | [assessment] | [misalignment] | [%] |
| Market pricing vs official | [bp] | [surprise gap] | [%] |

**Mistake Scenario Impact**

| Mistake | Duration Impact | Curve Impact | Credit Impact | FX Impact |
|---------|-----------------|--------------|---------------|-----------|
| Over-tightening | +50bp 10Y initially, -100bp later | Bull flattener then bull steepener | +30bp IG, +80bp HY | Currency strong then weak |
| Under-tightening | -20bp 10Y initially, +100bp later | Bear steepener | -10bp IG, +50bp HY | Currency weak then strong |
| Wrong timing | [varies] | [varies] | [varies] | [varies] |

**Policy Mistake Timeline**

| Phase | Duration | Rate Move | Credit | FX |
|-------|----------|-----------|--------|-----|
| Mistake made | [weeks] | [initial reaction] | [spread move] | [currency move] |
| Market recognizes | [weeks] | [corrective move] | [spread move] | [currency move] |
| CB pivots | [weeks] | [policy reversal] | [spread move] | [currency move] |
| Recovery | [months] | [normalization] | [spread move] | [currency move] |

**Policy Mistake Trades**

| Mistake Scenario | Initial Position | Pivot Position | Recovery Position |
|------------------|------------------|----------------|-------------------|
| Over-tightening | Short duration | Long duration (pivot) | Steepener (recovery) |
| Under-tightening | Long duration | Short duration (pivot) | Flattener (recovery) |
| Wrong timing | [varies] | [varies] | [varies] |

**Trade Recommendation**

Assessment:
- Mistake Probability: [%]
- Mistake Type: [type]
- Timing: [imminent / 1-3 months / 3-6 months]

Positioning:
- Pre-mistake: [position if anticipating]
- Mistake-made: [position on initial reaction]
- Pivot-anticipation: [position for reversal]
- Recovery: [position for normalization]

SOURCE: Bloomberg policy data + historical mistake analysis
```

---

## 三、极端场景分析

### 3.1 Tail Risk Scenario (尾部风险场景)

```
GOAL: Analyze tail risk scenario and position for extreme outcomes.

USER INPUT:
- Tail Scenario: [War escalation / Financial crisis / Pandemic / Major default / Political shock]
- Probability: [%]
- Impact Horizon: [Immediate / 1 week / 1 month / 3 months]

OUTPUT FORMAT:

**Scenario Description**

Scenario: {Description}
Trigger Probability: [%]
Impact Severity: [Mild / Moderate / Severe / Extreme]

**Immediate Impact (within 24 hours)**

| Asset | Pre-scenario | Post-scenario | Move | Mechanism |
|-------|--------------|---------------|------|-----------|
| VIX | [value] | [value] | [+pts] | Fear spike |
| OVX | [value] | [value] | [+pts] | Supply fear |
| USD Index | [value] | [value] | [%] | Safe-haven |
| Gold | [$] | [$] | [%] | Inflation/fear |
| US 10Y | [yield] | [yield] | [bp] | Flight to quality |
| IG Credit | [bp] | [bp] | [bp] | Risk-off widening |

**1-Week Impact**

| Asset | Day 1 | Day 7 | Weekly Move | Trend |
|-------|-------|-------|-------------|-------|
| [asset 1] | [value] | [value] | [move] | [direction] |
| [asset 2] | [value] | [value] | [move] | [direction] |

**Cross-Asset Transmission**

```
Trigger
→ [First Asset]: [move]
→ [Second Asset]: [move] (mechanism: correlation/functioning)
→ [Third Asset]: [move] (mechanism: [link])
→ [Final State]: [description]
```

**Historical Analog Comparison**

| Analog | Year | Similarity | Outcome | Recovery Time |
|--------|------|------------|---------|---------------|
| [event 1] | [year] | [% similar] | [impact summary] | [weeks/months] |
| [event 2] | [year] | [% similar] | [impact summary] | [weeks/months] |

**Tail Risk Positions**

| Position | Tail Risk Play | Recovery Play | Exit Trigger |
|----------|----------------|---------------|--------------|
| Duration | Long (quality) | Short (normalization) | Risk appetite return |
| FX | Long JPY/CHF | Short JPY/CHF | Stress easing |
| Credit | Long IG, Short HY | Long HY | Default fears ease |
| Vol | Long vol (calls) | Short vol | VIX normalization |
| Commodities | [scenario-specific] | [recovery] | Supply normalization |

**Risk Management**

Position Limits:
- Size: [% of normal] (tail positions may be larger/smaller)
- Stop: [level] (tail may not follow normal stops)
- Hedge: [protection] (hedge the hedge?)

SOURCE: Bloomberg real-time + historical analogs + scenario modeling
```

---

### 3.2 Black Swan Preparedness (黑天鹅准备)

```
GOAL: Portfolio preparedness for unpredictable black swan events.

OUTPUT FORMAT:

**Black Swan Categories**

| Category | Examples | Historical Impact | Probability |
|----------|----------|-------------------|-------------|
| Geopolitical | War, Sanctions, Regime change | [impact range] | [estimate] |
| Financial | Systemic failure, Major default | [impact range] | [estimate] |
| Natural | Pandemic, Natural disaster | [impact range] | [estimate] |
| Technological | Cyber, AI disruption | [impact range] | [estimate] |
| Political | Election shock, Policy reversal | [impact range] | [estimate] |

**Portfolio Black Swan Stress Test**

| Stress | Duration Impact | Credit Impact | FX Impact | Commodity Impact |
|--------|-----------------|---------------|-----------|------------------|
| War +50% | [+/- bp] | [+/- bp] | [%] | [%] |
| Pandemic V2 | [+/- bp] | [+/- bp] | [%] | [%] |
| Major Bank Failure | [+/- bp] | [+/- bp] | [%] | [%] |
| Cyber Infrastructure | [+/- bp] | [+/- bp] | [%] | [%] |

**Black Swan Protection Portfolio**

| Protection | Cost | Benefit in Crisis | Trigger |
|------------|------|-------------------|---------|
| Long VIX calls | [premium] | [payoff] | VIX > 40 |
| Long JPY | [carry cost] | [gain] | Risk-off |
| Long Gold | [no yield] | [gain] | Fear/inflation |
| Treasury cash optionality | [yield sacrifice] | [liquidity] | Market freeze |
| IG vs HY bias | [spread sacrifice] | [widening protection] | Credit stress |

**Cost of Protection**

| Strategy | Annual Cost | Expected Benefit | Net Expected Value |
|----------|-------------|------------------|--------------------|
| Full protection | [% of portfolio] | [estimated gain] | [negative/positive] |
| Partial protection | [%] | [gain] | [negative/positive] |
| No protection | 0 | [potential loss] | [risk accepted] |

**Protection Decision Framework**

Risk Tolerance: [High / Medium / Low]
- High: Minimal protection, accept tail risk
- Medium: Partial protection, key vulnerabilities
- Low: Full protection, comprehensive coverage

Key Vulnerabilities:
- [Exposure 1]: [protection recommendation]
- [Exposure 2]: [protection recommendation]
- [Exposure 3]: [protection recommendation]

SOURCE: Historical black swan analysis + scenario modeling
```

---

## 四、使用指南

| 主题 | 适用场景 | Prompt |
|------|----------|--------|
| **通胀交易** | CPI surprises, breakeven moves | Inflation Trade |
| **衰退交易** | Curve inversion, LEI decline | Recession Trade |
| **流动性危机** | Bid-ask widening, market freeze | Liquidity Crisis |
| **央行分歧** | Rate differential widening | CB Divergence |
| **政策失误** | Real rates extreme, guidance gap | Policy Mistake |
| **尾部风险** | Geopolitical escalation, tail event | Tail Risk |
| **黑天鹅准备** | Portfolio resilience check | Black Swan Prep |

---

**版本**: v0.1
**状态**: Ready for testing
**特色**: Macro theme-driven analysis