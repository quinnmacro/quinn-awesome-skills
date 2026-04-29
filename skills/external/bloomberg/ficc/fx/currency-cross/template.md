GOAL
Produce a currency pair analysis for {Currency Pair} with carry evaluation, central bank divergence pricing, and risk metrics.

TONE
Institutional FX trader — precise, carry-aware, macro-linked.

HEADINGS STYLE
Bold

STRUCTURE
1. Save as [{Currency Pair} Analysis].
2. Insert today's date and current time.
3. Present spot and forward structure as primary table.
4. Include rate differential, carry calculation, and technical levels.

ANALYSIS FRAMEWORK

SPOT AND FORWARD STRUCTURE

| Term | Rate | Forward Points | Implied Yield (%) |
|------|------|----------------|-------------------|
| Spot | [value] | - | - |
| 1M Forward | [value] | [value] | [annualized] |
| 3M Forward | [value] | [value] | [annualized] |
| 6M Forward | [value] | [value] | [annualized] |
| 12M Forward | [value] | [value] | [annualized] |

Comment on:
- Forward curve shape: ascending/descending (indicates carry sign)
- Points alignment with spot moves MTD

CARRY ANALYSIS

| Metric | Base Currency | Quote Currency | Differential |
|--------|---------------|----------------|--------------|
| Policy Rate | [value] | [value] | [diff in bp] |
| 10Y Bond Yield | [value] | [value] | [diff in bp] |
| Implied Carry (12M) | [value] | [value] | [total pips] |

Calculate:
- Annual carry from forward points: (Spot - 12M Forward) × 10,000 for USD pairs
- Break-even spot move: How much FX must move to erase carry
- Carry-to-vol ratio: Carry ÷ 3M realized volatility

CENTRAL BANK DIVERGENCE

| Central Bank | Current Rate | Next Meeting | Market Pricing | Bias |
|--------------|--------------|--------------|----------------|------|
| {Base CB} | [value] | [date] | [+/- bp] | [hawkish/dovish] |
| {Quote CB} | [value] | [date] | [+/- bp] | [hawkish/dovish] |

Comment on:
- Policy divergence direction: which CB more hawkish?
- Meeting timing asymmetry: who moves first?
- Market pricing vs official guidance gap

TECHNICAL LEVELS

| Level Type | Price | Significance |
|------------|-------|--------------|
| Resistance 1 | [value] | [prior high / trendline] |
| Resistance 2 | [value] | [prior high / trendline] |
| Current Spot | [value] | - |
| Support 1 | [value] | [prior low / trendline] |
| Support 2 | [value] | [prior low / trendline] |

| Momentum Indicator | Value | Signal |
|--------------------|-------|--------|
| RSI (14D) | [value] | [overbought/neutral/oversold] |
| MTD Move | [%] | [trend direction] |
| YTD Move | [%] | [trend direction] |
| 200-Day MA | [value] | [above/below] |

RISK METRICS

| Metric | Value | Interpretation |
|--------|-------|----------------|
| 3M Realized Vol | [%] | Historical volatility |
| 3M Implied Vol | [%] | Option market pricing |
| Vol Risk Premium | [bp] | Implied - Realized |
| 25D Risk Reversal | [bp] | Call skew vs Put skew |
| 25D Strangle | [bp] | Wing volatility premium |

Comment on:
- Is vol cheap or expensive vs history?
- Risk reversal direction: calls or puts bid?
- Hedging cost implication

KEY TAKEAWAYS

3-5 bullet points:
- Carry attractiveness (positive/negative, break-even)
- Policy divergence trade setup
- Technical position (near support/resistance?)
- Vol environment (cheap/expensive wings)
- Risk factors (data releases, political events)

SOURCE CITATIONS RULES

Every data point must cite source:
- "Bloomberg DAPI via [ticker]"
- "Central bank via Bloomberg News"
- "Option data via Bloomberg VCUB"

DATA RETRIEVAL METHOD

**Spot and Forward**
```
BDP("{Pair} Curncy", "PX_LAST")              # Spot
BDP("{Pair}1M Curncy", "PX_LAST")            # 1M forward
BDP("{Pair}3M Curncy", "PX_LAST")            # 3M forward
BDP("{Pair}6M Curncy", "PX_LAST")            # 6M forward
BDP("{Pair}12M Curncy", "PX_LAST")           # 12M forward
```

**Forward Points (if direct forwards unavailable)**
```
BDP("{Pair} Curncy", "FWD_POINTS_1M")
BDP("{Pair} Curncy", "FWD_POINTS_3M")
BDP("{Pair} Curncy", "FWD_POINTS_6M")
BDP("{Pair} Curncy", "FWD_POINTS_1Y")
```

**Volatility**
```
BDP("{Pair}3M Curncy", "VOLATILITY_3M")      # 3M implied vol
VCUB function for risk reversal and strangle
```

**Central Bank Rates**
```
# Major central bank tickers
FDTR             # Fed target rate
ECBDFR           # ECB deposit facility
BOJPOLICY        # BOJ policy balance rate
UKBRBASE         # BOE base rate
RBATCTR          # RBA cash rate target
```

TICKER MAPPING

| Pair | Spot Ticker | 3M Forward | 12M Forward |
|------|-------------|------------|-------------|
| EUR/USD | EURUSD Curncy | EURUSD3M Curncy | EURUSD12M Curncy |
| USD/JPY | USDJPY Curncy | USDJPY3M Curncy | USDJPY12M Curncy |
| GBP/USD | GBPUSD Curncy | GBPUSD3M Curncy | GBPUSD12M Curncy |
| AUD/USD | AUDUSD Curncy | AUDUSD3M Curncy | AUDUSD12M Curncy |
| USD/CNH | USDCNH Curncy | USDCNH3M Curncy | USDCNH12M Curncy |
| EUR/JPY | EURJPY Curncy | EURJPY3M Curncy | EURJPY12M Curncy |

TABLE REQUIREMENTS

1. Format: HTML tables
2. FX rates: 4 decimal places (2 for JPY pairs)
3. Forward points: integer or 2 decimals
4. Yields/vol: percentage with 1 decimal
5. Carry: expressed in pips and percentage

TEMPORAL PRIORITY RULES

1. TODAY: Spot, intraday range, momentum
2. MTD: Carry earned/paid, trend
3. 3M: Volatility metrics, technical levels
4. YTD: Macro trend context

GUIDELINES

1. Focus on actionable trade setup
2. Always show carry break-even math
3. Link FX moves to rate differential changes
4. Flag upcoming data/event risks
5. If data unavailable, note explicitly