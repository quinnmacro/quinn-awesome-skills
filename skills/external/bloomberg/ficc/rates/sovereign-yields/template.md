GOAL
Produce a sovereign yield curve analysis for {Country/Currency} with cross-country comparison and central bank policy pricing.

TONE
Institutional fixed income analyst — precise, data-driven, macro-aware.

HEADINGS STYLE
Bold

STRUCTURE
1. Save as [Country/Currency] Sovereign Yields Analysis.
2. Insert today's date and current time.
3. Present yield curve snapshot as the primary table.
4. Include cross-country spread comparison and FX linkage.

ANALYSIS FRAMEWORK

YIELD CURVE SNAPSHOT
Display current yield curve for {Country/Currency}:

| Maturity | Yield (%) | MTD Chg (bp) | YTD Chg (bp) |
|----------|-----------|--------------|--------------|
| 2Y | [value] | [value] | [value] |
| 5Y | [value] | [value] | [value] |
| 10Y | [value] | [value] | [value] |
| 30Y | [value] | [value] | [value] |

Calculate:
- 2Y-10Y spread (bp): curve steepness indicator
- 5Y-30Y spread (bp): long-end slope
- Comment on flattening/steepening trend

CENTRAL BANK POLICY PRICING

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Current Policy Rate | [value] | Central bank target |
| Market Implied Rate (1Y) | [value] | From futures/OIS |
| Rate Expectation | [+/- bp] | Direction and magnitude |
| Next Meeting Date | [date] | Scheduled decision |
| Cut/Hold/Hike Probability | [%] | Market-implied odds |

Comment on alignment between market pricing and central bank guidance.

CROSS-COUNTRY YIELD SPREADS
Compare {Country/Currency} 10Y yield against benchmarks:

| Spread Pair | Spread (bp) | MTD Chg | YTD Chg | Key Driver |
|-------------|-------------|---------|---------|------------|
| {Country/Currency}-US 10Y | [value] | [value] | [value] | [policy/inflation/fiscal] |
| {Country/Currency}-EUR 10Y | [value] | [value] | [value] | [policy/inflation/fiscal] |
| {Country/Currency}-JPY 10Y | [value] | [value] | [value] | [policy/inflation/fiscal] |

Retrieve comparison yields using same method as Primary:
- US 10Y: GT10 Govt
- EUR 10Y: GTDEM10Y Govt
- JPY 10Y: GJGB10 Index

Calculate spreads as: {Country/Currency} 10Y - Comparison 10Y (in bp)

FX LINKAGE
Show {Country/Currency} vs major FX pairs:

| FX Pair | Spot | MTD Chg (%) | Rate Diff (bp) | Carry (ann.) |
|---------|------|-------------|----------------|--------------|
| vs USD | [value] | [value] | [10Y spread] | [value] |
| vs EUR | [value] | [value] | [10Y spread] | [value] |
| vs JPY | [value] | [value] | [10Y spread] | [value] |

Comment on:
- FX-rate differential alignment
- Carry trade attractiveness
- Recent correlation breakdown if any

KEY TAKEAWAYS
3-5 bullet points summarizing:
- Main curve story
- Policy pricing implication
- Cross-country opportunity
- FX linkage insight
- Risk factors

SOURCE CITATIONS RULES
Every data point must include source citation. Use formats:
- "Bloomberg DAPI via [ticker]"
- "Central bank via Bloomberg"
- "Market data via Bloomberg"

DATA RETRIEVAL METHOD

For yield data with MTD/YTD changes, use one of these approaches:

**Method A: BQL (preferred)**
```
for(['GTDEM10Y Govt', 'GTDEM2Y Govt', ...])
get(pct_chg(yield(dates=MTD)), pct_chg(yield(dates=YTD)), yield)
with(fill=PREV)
```

**Method B: BDP with explicit change fields**
```
BDP("GTDEM10Y Govt", "YLD_YTM_MID")           # Current yield
BDP("GTDEM10Y Govt", "CHG_NET_1M")            # MTD change in bp
BDP("GTDEM10Y Govt", "CHG_NET_YTD")           # YTD change in bp
```

For countries where standard change fields are unavailable, use:
- `YLD_YTM_MID` for spot yield
- Calculate changes from `PX_CLOSE_1M` or `PX_CLOSE_YTD` if needed

DATA SOURCE MAPPING

| Country | 2Y Ticker | 5Y Ticker | 10Y Ticker | 30Y Ticker |
|---------|-----------|-----------|------------|------------|
| US | GT2 Govt | GT5 Govt | GT10 Govt | GT30 Govt |
| EUR (Germany) | GTDEM2Y Govt | GTDEM5Y Govt | GTDEM10Y Govt | GTDEM30Y Govt |
| JPY (Japan) | GJGB2 Index | GJGB5 Index | GJGB10 Index | GJGB30 Index |
| UK | GUKG2 Govt | GUKG5 Govt | GUKG10 Govt | GUKG30 Govt |
| AU | GACGB2 Govt | GACGB5 Govt | GACGB10 Govt | - |
| CN | CGB2Y Govt | - | CGB10Y Govt | - |

Note: JPY uses Index suffix (GJGB10 Index), others use Govt suffix

Policy Rate Tickers:
- Fed: FDTR, FEDL01
- ECB: ECBDFR
- BOJ: BOJPOLICY
- BOE: UKBRBASE
- RBA: RBATCTR

TABLE REQUIREMENTS
1. Format: HTML tables
2. Yields: percentage with 2 decimal places
3. Changes: basis points (bp), round to integer
4. FX rates: 4 decimal precision (2 for JPY)
5. Bold the 10Y row in yield curve table

TEMPORAL PRIORITY RULES
1. TODAY: Spot yields, intraday range
2. MTD: Month trend, policy shifts
3. YTD: Year context, major moves
4. Historical: 12-month range for spreads

GUIDELINES
1. Ensure insights are actionable for rates traders
2. Skip generic observations — focus on non-obvious
3. Always reference period for each data point
4. If data unavailable, note explicitly — do NOT fabricate
5. Check today's date before forming conclusions