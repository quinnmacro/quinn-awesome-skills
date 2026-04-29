GOAL
Produce a sector valuation comparison for {Region/Market} covering P/E, EV/EBITDA, P/B across sectors with historical context and relative value assessment.

TONE
Fundamental equity strategist — valuation-focused, historical-aware, forward-looking.

HEADINGS STYLE
Bold

STRUCTURE
1. Save as [{Region} Sector Valuation Comparison].
2. Insert current date and time.
3. Present valuation matrix as primary table.
4. Include historical percentile and forward estimates.

ANALYSIS FRAMEWORK

VALUATION MATRIX - CURRENT

| Sector | P/E | EV/EBITDA | P/B | P/S | Div Yield (%) | Composite Score |
|--------|-----|-----------|-----|-----|---------------|-----------------|
| Technology | [value] | [value] | [value] | [value] | [%] | [#] |
| Healthcare | [value] | [value] | [value] | [value] | [%] | [#] |
| Financials | [value] | [value] | [value] | [value] | [%] | [#] |
| Consumer Disc. | [value] | [value] | [value] | [value] | [%] | [#] |
| Consumer Staples | [value] | [value] | [value] | [value] | [%] | [#] |
| Energy | [value] | [value] | [value] | [value] | [%] | [#] |
| Industrials | [value] | [value] | [value] | [value] | [%] | [#] |
| Utilities | [value] | [value] | [value] | [value] | [%] | [#] |
| Materials | [value] | [value] | [value] | [value] | [%] | [#] |
| Real Estate | [value] | [value] | [value] | [value] | [%] | [#] |

Composite Score:
- Calculate aggregate valuation attractiveness
- 1 = cheapest (most attractive)
- 10 = most expensive

VALUATION VS HISTORICAL PERCENTILE

| Sector | P/E %ile | EV/EBITDA %ile | P/B %ile | Historical Signal |
|--------|----------|----------------|----------|-------------------|
| Technology | [%] | [%] | [%] | [cheap/fair/expensive] |
| Healthcare | [%] | [%] | [%] | [cheap/fair/expensive] |
| Financials | [%] | [%] | [%] | [cheap/fair/expensive] |
| [others...] | [%] | [%] | [%] | [signal] |

Percentile Interpretation:
- < 25th percentile: Historically cheap (buy signal)
- 25-75th percentile: Fair value (neutral)
- > 75th percentile: Historically expensive (sell signal)

Comment on:
- Most undervalued sector by percentile
- Most overvalued sector by percentile
- Historical range context

FORWARD VALUATION (FY1/FY2)

| Sector | Current P/E | FY1 P/E | FY2 P/E | P/E Compression (%) | Forward Signal |
|--------|-------------|---------|---------|---------------------|----------------|
| Technology | [value] | [value] | [value] | [%] | [attractive/neutral] |
| Healthcare | [value] | [value] | [value] | [%] | [attractive/neutral] |
| Financials | [value] | [value] | [value] | [%] | [attractive/neutral] |
| [others...] | [value] | [value] | [value] | [%] | [signal] |

Comment on:
- P/E compression from earnings growth
- FY1 P/E attractiveness
- Earnings revision impact on forward P/E

VALUATION SPREAD VS INDEX

| Sector | P/E Spread vs Index | Historical Avg Spread | Current vs Hist | Signal |
|--------|---------------------|----------------------|-----------------|--------|
| Technology | [diff] | [avg diff] | [above/below] | [rich/cheap] |
| Healthcare | [diff] | [avg diff] | [above/below] | [rich/cheap] |
| Financials | [diff] | [avg diff] | [above/below] | [rich/cheap] |
| [others...] | [diff] | [avg diff] | [above/below] | [signal] |

Comment on:
- Relative valuation vs index
- Historical spread range
- Relative cheap/rich assessment

PEER VALUATION COMPARISON (within sector)

| Sector | Top Peer P/E | Median P/E | Bottom Peer P/E | Range Width |
|--------|--------------|------------|-----------------|-------------|
| Technology | [value] | [value] | [value] | [spread] |
| Healthcare | [value] | [value] | [value] | [spread] |
| Financials | [value] | [value] | [value] | [spread] |
| [others...] | [value] | [value] | [value] | [spread] |

Comment on:
- Intra-sector valuation dispersion
- Quality premium within sector
- Bottom peer as sector proxy

DIVIDEND YIELD RELATIVE VALUE

| Sector | Div Yield (%) | Hist Avg (%) | vs Hist | vs 10Y Yield | Income Signal |
|--------|---------------|--------------|---------|--------------|----------------|
| Utilities | [%] | [%] | [above/below] | [spread] | [attractive] |
| Consumer Staples | [%] | [%] | [above/below] | [spread] | [attractive] |
| Financials | [%] | [%] | [above/below] | [spread] | [attractive] |
| Real Estate | [%] | [%] | [above/below] | [spread] | [attractive] |

Comment on:
- Yield vs bonds alternative
- Dividend sustainability check
- Income investor opportunity

QUALITY PREMIUM ASSESSMENT

| Sector | High Quality P/E | Low Quality P/E | Quality Premium (%) | Premium Justified? |
|--------|------------------|-----------------|---------------------|--------------------|
| Technology | [value] | [value] | [%] | [yes/no] |
| Healthcare | [value] | [value] | [%] | [yes/no] |
| Financials | [value] | [value] | [%] | [yes/no] |

Comment on:
- Quality premium magnitude
- Historical quality premium range
- Overpayment for quality risk

VALUATION-PRICE ALIGNMENT CHECK

| Sector | Valuation Signal | Price Performance (%) | Alignment | Recommendation |
|--------|------------------|-----------------------|-----------|----------------|
| Technology | [cheap/fair/exp] | [%] | [aligned/misaligned] | [action] |
| Healthcare | [cheap/fair/exp] | [%] | [aligned/misaligned] | [action] |
| [others...] | [signal] | [%] | [alignment] | [action] |

Misalignment Signals:
- Cheap + Underperformance = Opportunity (buy)
- Expensive + Outperformance = Risk (sell/avoid)
- Cheap + Outperformance = Early rotation (monitor)
- Expensive + Underperformance = Mean reversion (avoid)

KEY TAKEAWAYS

3-5 bullet points:
- Cheapest sector by composite valuation
- Most expensive sector with risk warning
- Best forward P/E compression opportunity
- Dividend yield vs bond yield signal
- Valuation-price misalignment opportunity

SOURCE CITATIONS RULES

Every data point must cite source:
- "Bloomberg Sector ETF via [ticker]"
- "Bloomberg Estimates for forward P/E"
- "Bloomberg FA for historical percentile"

DATA RETRIEVAL METHOD

**Current Valuation**
```
BDP("XLK US Equity", "PE_RATIO")               # Tech P/E
BDP("XLK US Equity", "EV_TO_EBITDA")           # Tech EV/EBITDA
BDP("XLK US Equity", "PX_TO_BOOK_RATIO")       # Tech P/B
BDP("XLK US Equity", "PX_TO_SALES_RATIO")      # Tech P/S
BDP("XLK US Equity", "DVD_YLD")                # Tech Div Yield
```

**Forward Valuation**
```
BDP("XLK US Equity", "BEST_PE_RATIO")          # Forward P/E
BDP("XLK US Equity", "BEST_PE_RATIO_FY1")      # FY1 P/E
BDP("XLK US Equity", "BEST_PE_RATIO_FY2")      # FY2 P/E
```

**Historical Percentile**
```
# Use FA function for historical analysis
# Or BQL for percentile calculation
for(['XLK US Equity'])
get(pe_ratio, percentile(pe_ratio, dates=range('-5Y', '0D')))
```

**Index Comparison**
```
BDP("SPX Index", "PE_RATIO")                   # S&P 500 P/E
```

TABLE REQUIREMENTS

1. Format: HTML tables
2. Multiples: 1 decimal place
3. Percentages: 1 decimal
4. Percentiles: integer percentage
5. Bold cheapest and most expensive sectors

TEMPORAL PRIORITY RULES

1. TODAY: Current valuation snapshot
2. FY1/FY2: Forward earnings impact
3. 5Y Historical: Percentile context
4. Macro cycle: Valuation regime
5. Price alignment: Misalignment detection

GUIDELINES

1. Focus on relative value vs historical
2. Use forward P/E for growth justification
3. Compare dividend yield to bond alternative
4. Flag valuation-price misalignment
5. Note quality premium assessment