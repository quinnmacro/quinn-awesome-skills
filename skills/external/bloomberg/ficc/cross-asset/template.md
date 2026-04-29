GOAL
Produce a cross-asset linkage analysis showing transmission paths between Rates, FX, Credit, and Commodities for {Primary Theme/Region}.

TONE
Macro strategist — linkage-aware, narrative-driven, risk-focused.

HEADINGS STYLE
Bold

STRUCTURE
1. Save as [Cross-Asset Analysis: {Theme}].
2. Insert today's date and current time.
3. Present macro backdrop as context.
4. Show asset-to-asset transmission chains.

ANALYSIS FRAMEWORK

MACRO BACKDROP

| Indicator | Value | Trend | Surprise Index |
|-----------|-------|-------|----------------|
| {Region} GDP Growth | [%] | [accelerating/slowing] | [vs consensus] |
| {Region} CPI Inflation | [%] | [rising/falling] | [vs consensus] |
| {Region} PMI | [value] | [expansion/contraction] | [vs expectations] |
| Global Risk Appetite | [index] | [risk-on/risk-off] | - |
| VIX | [value] | [calm/stressed] | - |

Narrative summary:
- What is the dominant macro theme today?
- Which data point drove recent market moves?

RATES → FX TRANSMISSION

| Link | Rates Driver | FX Impact | Correlation Check |
|------|--------------|-----------|-------------------|
| Rate Differential | [10Y spread bp] | [FX pair move %] | [aligned/diverged] |
| Policy Expectation | [rate path change] | [currency strength] | [aligned/diverged] |
| Real Yield | [inflation-adjusted] | [currency appeal] | [aligned/diverged] |

Calculate:
- Has FX move matched rate differential change?
- Correlation breakdown: when/why?

Comment on:
- Carry trade positioning signal
- Safe-haven vs yield-seeking flow balance

FX → CREDIT TRANSMISSION

| Link | FX Driver | Credit Impact | Mechanism |
|------|-----------|---------------|-----------|
| USD Strength | [% move] | [EM credit spread chg] | [dollar debt burden] |
| {Regional} FX | [% move] | [local credit chg] | [currency mismatch] |
| Funding Currency | [JPY/EUR move] | [carry trade credit] | [funding cost] |

Highlight:
- EM credit sensitivity to USD
- Currency mismatch risk in specific regions
- Funding currency effect on carry trades

CREDIT → COMMODITIES TRANSMISSION

| Link | Credit Driver | Commodity Impact | Mechanism |
|------|---------------|------------------|-----------|
| Energy Credit Spreads | [bp chg] | [oil price %] | [sector health signal] |
| HY Distress | [default rate] | [commodity demand] | [demand destruction] |
| IG Issuance | [$bn] | [project financing] | [capex funding] |

Comment on:
- Energy credit as oil demand proxy
- HY stress signaling commodity demand risk

COMMODITIES → RATES TRANSMISSION

| Link | Commodity Driver | Rates Impact | Mechanism |
|------|------------------|--------------|-----------|
| Oil Price | [% move] | [inflation expectation] | [CPI impulse] |
| Energy Curve | [contango/back] | [policy timing] | [supply shock signal] |
| Food Prices | [% move] | [emerging rates] | [inflation pass-through] |

Calculate:
- Oil-to-inflation transmission lag
- Energy shock policy response probability

RISK APPETITE SYNTHESIS

| Asset | Risk Signal | Current State | Direction |
|-------|-------------|---------------|-----------|
| VIX | Equity fear | [value] | [↑/↓] |
| IG-HY Spread Ratio | Credit risk | [ratio] | [↑/↓] |
| USD vs EM FX | Flight-to-quality | [index] | [↑/↓] |
| Gold | Inflation/geopolitical | [price] | [↑/↓] |
| Curve Slope | Growth fear | [2Y-10Y] | [↑/↓] |

Risk Regime Assessment:
- Risk-on: narrow spreads, weak USD, steep curve, low VIX
- Risk-off: wide spreads, strong USD, flat curve, high VIX
- Current regime: [specify]

KEY TRANSMISSION CHAIN

Identify dominant chain today:

```
[Primary Driver] → [Secondary Asset] → [Third Asset] → [Final Impact]

Example: Oil +5% → Inflation Expectation ↑ → Rates +10bp → USD +0.5%
```

Comment on:
- Where in transmission chain we are today
- Which link is weakest (most likely to break)
- Amplification or dampening factors

KEY TAKEAWAYS

3-5 bullet points:
- Dominant macro narrative
- Strongest transmission link today
- Weakest/broken correlation
- Risk regime classification
- What could flip the chain direction

SOURCE CITATIONS RULES

Every data point must cite source:
- "Bloomberg DAPI via [ticker]"
- "Macro data via Bloomberg ECO"
- "Risk indices via Bloomberg"

DATA RETRIEVAL METHOD

**Macro Data**
```
# Economic indicators
BDP("{Region}GDP Index", "PX_LAST")
BDP("{Region}CPI Index", "PX_LAST")
BDP("{Region}PMI Index", "PX_LAST")

# Surprise indices
ECO function for economic surprise
```

**Risk Appetite**
```
BDP("VIX Index", "PX_LAST")
BDP("GOLDSPT Index", "PX_LAST")
# Use custom risk appetite index if available
```

**Cross-Asset Core**
```
# Rates
GT10 Govt           # US 10Y
GTDEM10Y Govt       # EUR 10Y

# FX
EURUSD Curncy
USDCNH Curncy

# Credit
LCGDTRUU Index      # US IG
HLHO Index          # US HY

# Commodities
CL1 Comdty          # WTI front
```

TABLE REQUIREMENTS

1. Format: HTML tables
2. Percentages: 1-2 decimals
3. Spreads: basis points (bp)
4. Correlation: aligned/diverged assessment
5. Bold key transmission metrics

TEMPORAL PRIORITY RULES

1. TODAY: Current cross-asset snapshot
2. MTD: Transmission evolution
3. YTD: Correlation stability assessment
4. Cycle: Regime context

GUIDELINES

1. Show causation chain, not just correlation
2. Identify which link is breaking
3. Use narrative to connect numbers
4. Classify risk regime explicitly
5. Always anchor to macro backdrop