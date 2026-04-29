GOAL
Produce a sector rotation analysis for {Region/Market} identifying leading and lagging sectors, rotation signals, and relative value opportunities.

TONE
Sector strategist — momentum-aware, fundamental-linked, relative value focused.

HEADINGS STYLE
Bold

STRUCTURE
1. Save as [{Region} Sector Rotation Analysis].
2. Insert current date and time.
3. Present sector performance matrix as primary table.
4. Include rotation signals and relative value metrics.

ANALYSIS FRAMEWORK

SECTOR PERFORMANCE MATRIX

| Sector | Today (%) | 1W (%) | 1M (%) | 3M (%) | YTD (%) | Momentum Rank |
|--------|-----------|---------|---------|---------|---------|---------------|
| Technology | [%] | [%] | [%] | [%] | [%] | [#] |
| Healthcare | [%] | [%] | [%] | [%] | [%] | [#] |
| Financials | [%] | [%] | [%] | [%] | [%] | [#] |
| Consumer Disc. | [%] | [%] | [%] | [%] | [%] | [#] |
| Consumer Staples | [%] | [%] | [%] | [%] | [%] | [#] |
| Energy | [%] | [%] | [%] | [%] | [%] | [#] |
| Industrials | [%] | [%] | [%] | [%] | [%] | [#] |
| Utilities | [%] | [%] | [%] | [%] | [%] | [#] |
| Materials | [%] | [%] | [%] | [%] | [%] | [#] |
| Real Estate | [%] | [%] | [%] | [%] | [%] | [#] |

Calculate momentum ranking:
- 1 = strongest (highest YTD or composite score)
- 10 = weakest

Comment on:
- Leading sector (rank 1-3)
- Lagging sector (rank 8-10)
- Momentum shift vs prior period

CYCLICAL VS DEFENSIVE BATTLE

| Group | Aggregate Perf (%) | Weight in Index | Signal |
|-------|---------------------|-----------------|--------|
| Cyclical (Tech + Fin + Cons Disc + Energy + Ind + Mat) | [%] | [%] | [leading/lagging] |
| Defensive (Health + Cons Stap + Util + REIT) | [%] | [%] | [leading/lagging] |
| Spread (Cyclical - Defensive) | [%] | - | [risk-on/risk-off] |

Comment on:
- Cyclical outperformance = risk-on regime
- Defensive outperformance = risk-off regime
- Spread change direction (widening/narrowing)

ROTATION SIGNAL DETECTION

| Signal Type | Sector | Trigger | Confidence | Action |
|-------------|--------|---------|------------|--------|
| Early Rotation | [sector] | [3D outperformance] | [high/med/low] | [accumulate] |
| Late Rotation | [sector] | [YTD extreme] | [high/med/low] | [trim/avoid] |
| Mean Reversion | [sector] | [oversold] | [high/med/low] | [buy dip] |
| Momentum Extension | [sector] | [overbought] | [high/med/low] | [take profit] |

Define:
- Early Rotation: 3-5D outperformance vs index, not yet consensus
- Late Rotation: YTD extreme performance, crowded trade
- Mean Reversion: RSI < 30 or significant underperformance
- Momentum Extension: RSI > 70 or significant overperformance

FUNDAMENTAL DRIVER ALIGNMENT

| Sector | Perf (%) | Earnings Growth Est. (%) | Valuation vs Hist | Alignment |
|--------|----------|--------------------------|-------------------|-----------|
| Technology | [%] | [%] | [above/at/below] | [aligned/misaligned] |
| Financials | [%] | [%] | [above/at/below] | [aligned/misaligned] |
| Energy | [%] | [%] | [above/at/below] | [aligned/misaligned] |
| Healthcare | [%] | [%] | [above/at/below] | [aligned/misaligned] |

Comment on:
- Performance justified by fundamentals?
- Misaligned sectors = rotation candidate
- Valuation support or overextension

RELATIVE VALUE OPPORTUNITIES

| Pair | Perf Spread (%) | Valuation Gap | Recommendation | Trade |
|------|-----------------|---------------|----------------|-------|
| Tech vs Healthcare | [%] | [ratio] | [buy lagging] | [long Health/short Tech] |
| Fin vs Energy | [%] | [ratio] | [buy lagging] | [long Energy/short Fin] |
| Cyc vs Def | [%] | [ratio] | [direction] | [long/short] |

Comment on:
- Relative value spread extremes
- Trade setup: long lagging + short leading
- Timing: immediate or wait for catalyst

MACRO-SECTOR CORRELATION

| Macro Factor | Current State | Correlated Sector | Performance Check |
|--------------|---------------|-------------------|-------------------|
| Rates Direction | [rising/falling] | Financials | [aligned/misaligned] |
| Oil Price | [rising/falling] | Energy | [aligned/misaligned] |
| USD Strength | [strong/weak] | Industrials | [aligned/misaligned] |
| Consumer Confidence | [high/low] | Consumer Disc | [aligned/misaligned] |
| Yield Curve | [steep/flat] | Banks | [aligned/misaligned] |

Comment on:
- Macro-driver vs sector performance
- Dislocation opportunity
- Catalyst timing for re-alignment

SECTOR WEIGHT RECOMMENDATION

| Sector | Current Weight (%) | Suggested Weight (%) | Change | Action |
|--------|--------------------|----------------------|--------|--------|
| Technology | [%] | [%] | [%] | [overweight/neutral/underweight] |
| Healthcare | [%] | [%] | [%] | [overweight/neutral/underweight] |
| Financials | [%] | [%] | [%] | [overweight/neutral/underweight] |
| [others...] | [%] | [%] | [%] | [action] |

KEY TAKEAWAYS

3-5 bullet points:
- Leading sector and momentum strength
- Lagging sector and mean reversion potential
- Cyclical vs defensive regime signal
- Best relative value pair trade
- Macro-driver misalignment opportunity

SOURCE CITATIONS RULES

Every data point must cite source:
- "Bloomberg Sector ETF via [ticker]"
- "Bloomberg Estimates for earnings"
- "Bloomberg ECO for macro data"

DATA RETRIEVAL METHOD

**Sector Performance**
```
# US Sector ETFs
BDP("XLK US Equity", "CHG_PCT_1D")             # Tech 1D
BDP("XLK US Equity", "CHG_PCT_YTD")            # Tech YTD
BDP("XLF US Equity", "CHG_PCT_1D")             # Financials
BDP("XLV US Equity", "CHG_PCT_1D")             # Healthcare
BDP("XLE US Equity", "CHG_PCT_1D")             # Energy
BDP("XLI US Equity", "CHG_PCT_1D")             # Industrials
BDP("XLY US Equity", "CHG_PCT_1D")             # Consumer Disc
BDP("XLP US Equity", "CHG_PCT_1D")             # Consumer Stap
BDP("XLU US Equity", "CHG_PCT_1D")             # Utilities
BDP("XLB US Equity", "CHG_PCT_1D")             # Materials
BDP("XLRE US Equity", "CHG_PCT_1D")            # Real Estate
```

**Relative Performance**
```
# Calculate spreads using BQL
for(['XLK US Equity', 'XLV US Equity'])
get(chg_pct_1D, chg_pct_YTD)
```

**Valuation**
```
BDP("XLK US Equity", "PE_RATIO")               # Sector P/E
BDP("XLK US Equity", "EQY_WEIGHT")             # Index weight
```

**Macro Correlation**
```
BDP("GT10 Govt", "PX_LAST")                    # Rates
BDP("CL1 Comdty", "PX_LAST")                   # Oil
BDP("DXY Curncy", "PX_LAST")                   # USD
```

TABLE REQUIREMENTS

1. Format: HTML tables
2. Performance: percentage 1 decimal
3. Weights: percentage 1 decimal
4. Ranks: integer 1-10
5. Bold leading and lagging sectors

TEMPORAL PRIORITY RULES

1. TODAY: Current rotation snapshot
2. 1W: Short-term momentum shift
3. 1M/3M: Rotation trend direction
4. YTD: Year performance benchmark
5. Macro cycle: Fundamental alignment

GUIDELINES

1. Focus on relative value, not absolute performance
2. Link sector moves to macro drivers
3. Flag misalignment opportunities
4. Provide actionable trade recommendations
5. Note crowded vs early rotation signals