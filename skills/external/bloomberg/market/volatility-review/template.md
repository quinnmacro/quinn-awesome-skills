GOAL
Produce a cross-asset volatility review covering equity VIX, FX vol, rates vol, and credit vol for {Market/Region}.

TONE
Volatility strategist — risk-aware, regime-focused, cross-asset linked.

HEADINGS STYLE
Bold

STRUCTURE
1. Save as [{Region} Volatility Review].
2. Insert current date and time.
3. Present VIX and equity vol as primary table.
4. Include FX, rates, and credit vol comparison.

ANALYSIS FRAMEWORK

EQUITY VOLATILITY SNAPSHOT

| Index | VIX Level | 1D Chg | 1W Chg | 3M Avg | Regime Signal |
|-------|-----------|--------|--------|--------|---------------|
| {Primary VIX} | [value] | [%] | [%] | [avg] | [calm/moderate/stressed] |
| VIX (US) | [value] | [%] | [%] | [avg] | [global reference] |
| VSTOXX (EU) | [value] | [%] | [%] | [avg] | [EU sentiment] |
| VIXJ (JP) | [value] | [%] | [%] | [avg] | [JP sentiment] |

Regime Classification:
- CALM: VIX < 15, risk-on environment
- MODERATE: VIX 15-25, normal uncertainty
- STRESSED: VIX > 25, risk-off environment

Comment on:
- Current regime vs 3M average
- Regional divergence (US vs EU vs JP)
- VIX spike or compression signal

FX VOLATILITY MATRIX

| Pair | 1M Imp Vol (%) | 3M Imp Vol (%) | Realized 3M (%) | Vol Premium (bp) |
|------|----------------|----------------|-----------------|------------------|
| EUR/USD | [%] | [%] | [%] | [value] |
| USD/JPY | [%] | [%] | [%] | [value] |
| GBP/USD | [%] | [%] | [%] | [value] |
| AUD/USD | [%] | [%] | [%] | [value] |
| USD/CNH | [%] | [%] | [%] | [value] |

Calculate:
- Vol Premium: Implied - Realized
- Premium > 0: vol expensive (good to sell)
- Premium < 0: vol cheap (good to buy)

Comment on:
- FX vol relative to equity vol
- Safe-haven pairs vs carry pairs
- Hedging cost assessment

RATES VOLATILITY CHECK

| Instrument | 1M Vol | 3M Vol | Realized 3M | Steepener Vol |
|------------|--------|--------|-------------|---------------|
| 10Y Yield {Country} | [bp/day] | [bp/day] | [bp/day] | [bp/day] |
| 2Y-10Y Spread | [bp/day] | [bp/day] | [bp/day] | [bp/day] |
| US 10Y Yield | [bp/day] | [bp/day] | [bp/day] | [reference] |

Comment on:
- Rates vol vs FX vol
- Curve vol for steepener/flattener trades
- Central bank event vol spike

COMMODITY VOLATILITY

| Commodity | Vol Index | 1M Imp Vol (%) | 3M Imp Vol (%) | Regime |
|-----------|-----------|----------------|----------------|--------|
| Oil (OVX) | [value] | [%] | [%] | [calm/stressed] |
| Gold (GVZ) | [value] | [%] | [%] | [calm/stressed] |
| Silver (VXSLV) | [value] | [%] | [%] | [calm/stressed] |

Comment on:
- Commodity vol vs equity vol
- Energy vol spike signals
- Gold vol as inflation/fear proxy

CREDIT VOLATILITY IMPLIED

| Instrument | Index Spread | Imp Vol Equivalent | Distress Signal |
|------------|--------------|--------------------|-----------------|
| IG CDS Index | [bp] | [vol proxy] | [low risk] |
| HY CDS Index | [bp] | [vol proxy] | [moderate risk] |
| EM CDS Index | [bp] | [vol proxy] | [elevated risk] |

Comment on:
- Credit vol vs equity vol
- HY spread as equity fear proxy
- IG spread as rates vol proxy

VOL TERM STRUCTURE

| Asset | 1M Vol | 3M Vol | 6M Vol | 12M Vol | Term Slope |
|-------|--------|--------|--------|---------|------------|
| VIX | [%] | [%] | [%] | [%] | [upward/flat/downward] |
| EUR/USD | [%] | [%] | [%] | [%] | [upward/flat/downward] |
| 10Y Yield | [bp] | [bp] | [bp] | [bp] | [upward/flat/downward] |

Comment on:
- Term structure signal:
  - Upward: expected vol increase (buy long-dated)
  - Downward: vol expected to fall (buy short-dated)
- Event pricing in term structure

RISK REVERSAL CHECK

| Asset | 25D Call Vol | 25D Put Vol | Risk Reversal (bp) | Skew Signal |
|-------|--------------|-------------|--------------------|--------------|
| {Primary Index} | [%] | [%] | [value] | [calls bid/puts bid] |
| EUR/USD | [%] | [%] | [value] | [calls bid/puts bid] |
| USD/JPY | [%] | [%] | [value] | [calls bid/puts bid] |

Comment on:
- Skew direction: upside vs downside fear
- Equity skew vs FX skew consistency
- Hedging bias (protect downside vs upside)

VOL CORRELATION MATRIX

| Pair | Correlation | Divergence Signal | Explanation |
|------|-------------|--------------------|-------------|
| VIX vs OVX | [value] | [aligned/diverged] | [energy-risk link] |
| VIX vs FX Vol | [value] | [aligned/diverged] | [cross-asset fear] |
| VIX vs Rates Vol | [value] | [aligned/diverged] | [policy uncertainty] |
| VIX vs HY Spread | [value] | [aligned/diverged] | [credit-equity link] |

KEY TAKEAWAYS

3-5 bullet points:
- Current volatility regime (calm/moderate/stressed)
- Cross-asset vol alignment or divergence
- Vol cheap/expensive by asset class
- Term structure trade signal
- Risk reversal skew direction

SOURCE CITATIONS RULES

Every data point must cite source:
- "Bloomberg Vol via [ticker]"
- "Bloomberg VCUB for FX vol"
- "Bloomberg SWPM for rates vol"

DATA RETRIEVAL METHOD

**Equity Vol**
```
BDP("VIX Index", "PX_LAST")                    # VIX level
BDP("VIX Index", "CHG_PCT_1D")                 # Daily change
BDP("VSTOXX Index", "PX_LAST")                 # EU VIX
BDP("VIXJ Index", "PX_LAST")                   # JP VIX
```

**FX Vol**
```
VCUB function for implied vol surface
BDP("EURUSD3M Curncy", "VOLATILITY_3M")        # 3M implied vol
```

**Commodity Vol**
```
BDP("OVX Index", "PX_LAST")                    # Oil vol
BDP("GVZ Index", "PX_LAST")                    # Gold vol
```

**Credit**
```
BDP("CDXIG5 Gen 5Y", "PX_SPREAD")              # IG CDS
BDP("CDXHY5 Gen 5Y", "PX_SPREAD")              # HY CDS
```

TABLE REQUIREMENTS

1. Format: HTML tables
2. Vol levels: percentage 1 decimal
3. Vol premiums: basis points
4. Correlations: 2 decimals
5. Bold primary VIX row

TEMPORAL PRIORITY RULES

1. TODAY: Current vol levels, regime
2. 1W: Short-term vol trend
3. 3M: Average vol context
4. YTD: Vol history benchmark
5. Term structure: Forward vol pricing

GUIDELINES

1. Classify volatility regime explicitly
2. Compare cross-asset vol levels
3. Highlight vol premium opportunities
4. Use term structure for timing trades
5. Link risk reversal to sentiment