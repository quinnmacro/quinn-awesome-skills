GOAL
Produce a equity market morning briefing for {Region/Market} covering key indices, sector performance, and notable stock movers.

TONE
Morning equity strategist — concise, momentum-aware, catalyst-focused.

HEADINGS STYLE
Bold

STRUCTURE
1. Save as [{Region/Market} Equity Morning Brief].
2. Insert current date and time (pre-market or early trading).
3. Present index snapshot as primary table.
4. Include sector rotation and top movers.

ANALYSIS FRAMEWORK

INDEX LEVELS SNAPSHOT

| Index | Level | Chg (%) | Chg (pts) | YTD (%) | Key Driver |
|-------|-------|---------|-----------|---------|------------|
| {Primary Index} | [value] | [%] | [pts] | [%] | [driver] |
| {Secondary Index} | [value] | [%] | [pts] | [%] | [driver] |
| S&P 500 | [value] | [%] | [pts] | [%] | [reference] |
| VIX | [value] | [%] | [pts] | [%] | [fear gauge] |

Comment on:
- Index correlation with global markets
- VIX signal: risk-on vs risk-off regime

SECTOR ROTATION MATRIX

| Sector | Today (%) | 5D (%) | MTD (%) | Momentum Signal |
|--------|-----------|---------|---------|------------------|
| Technology | [%] | [%] | [%] | [leading/lagging] |
| Healthcare | [%] | [%] | [%] | [leading/lagging] |
| Financials | [%] | [%] | [%] | [leading/lagging] |
| Consumer | [%] | [%] | [%] | [leading/lagging] |
| Energy | [%] | [%] | [%] | [leading/lagging] |
| Industrials | [%] | [%] | [%] | [leading/lagging] |
| Utilities | [%] | [%] | [%] | [leading/lagging] |

Highlight:
- Best performing sector today
- Worst performing sector today
- Rotation pattern: defensive vs cyclical

TOP MOVERS - GAINERS

| Ticker | Company | Chg (%) | Volume | Catalyst |
|--------|---------|---------|--------|----------|
| {Ticker 1} | [name] | [%] | [x avg] | [earnings/news/sector] |
| {Ticker 2} | [name] | [%] | [x avg] | [earnings/news/sector] |
| {Ticker 3} | [name] | [%] | [x avg] | [earnings/news/sector] |
| {Ticker 4} | [name] | [%] | [x avg] | [earnings/news/sector] |
| {Ticker 5} | [name] | [%] | [x avg] | [earnings/news/sector] |

TOP MOVERS - LOSERS

| Ticker | Company | Chg (%) | Volume | Catalyst |
|--------|---------|---------|--------|----------|
| {Ticker 1} | [name] | [%] | [x avg] | [earnings/news/sector] |
| {Ticker 2} | [name] | [%] | [x avg] | [earnings/news/sector] |
| {Ticker 3} | [name] | [%] | [x avg] | [earnings/news/sector] |
| {Ticker 4} | [name] | [%] | [x avg] | [earnings/news/sector] |
| {Ticker 5} | [name] | [%] | [x avg] | [earnings/news/sector] |

Comment on:
- Earnings-driven vs sector-driven movers
- Volume confirmation of conviction
- News catalyst details

OPTIONS FLOW CHECK

| Metric | Value | Signal |
|--------|-------|--------|
| Put/Call Ratio (Overall) | [ratio] | [bearish/bullish] |
| Unusual Call Activity | [ticker] | [bullish bet] |
| Unusual Put Activity | [ticker] | [hedging/bearish] |
| Implied Vol Change | [%] | [expectation shift] |

Comment on:
- Options positioning vs spot market
- Unusual activity as directional signal

MACRO CATALYSTS TODAY

| Catalyst | Time | Expectation | Market Impact |
|----------|------|-------------|---------------|
| {Economic Data} | [time] | [consensus] | [potential reaction] |
| {Fed/CB Speech} | [time] | [topic] | [potential reaction] |
| {Corporate Event} | [time] | [company] | [potential reaction] |

Highlight:
- Key risk events for session
- Data surprise scenarios

KEY TAKEAWAYS

3-5 bullet points:
- Index direction and conviction
- Sector rotation theme
- Top mover catalyst summary
- Options positioning signal
- Macro catalyst watchlist

SOURCE CITATIONS RULES

Every data point must cite source:
- "Bloomberg Index via [ticker]"
- "Bloomberg NEWS for catalysts"
- "Bloomberg MOV for movers"

DATA RETRIEVAL METHOD

**Indices**
```
BDP("{Primary Index}", "PX_LAST")              # Current level
BDP("{Primary Index}", "CHG_PCT_1D")           # Daily change
BDP("{Primary Index}", "CHG_PCT_YTD")          # YTD change
BDP("VIX Index", "PX_LAST")                    # VIX level
```

**Sector Indices**
```
# US sector ETFs or indices
XLK US Equity      # Technology
XLF US Equity      # Financials
XLV US Equity      # Healthcare
XLE US Equity      # Energy
XLI US Equity      # Industrials
XLY US Equity      # Consumer Discretionary
XLP US Equity      # Consumer Staples
XLU US Equity      # Utilities
```

**Top Movers**
```
MOV function for top gainers/losers
BDP("{Ticker}", "CHG_PCT_1D")
BDP("{Ticker}", "VOLUME")
```

**Options**
```
OI MON function for options activity
VOL function for implied vol
```

TABLE REQUIREMENTS

1. Format: HTML tables
2. Index levels: integer or 2 decimals
3. Changes: percentage with 1 decimal
4. Volume: x times average
5. Bold primary index row

TEMPORAL PRIORITY RULES

1. TODAY: Index snapshot, top movers
2. 5D: Short-term momentum
3. MTD: Month performance context
4. YTD: Year performance benchmark

GUIDELINES

1. Keep briefing concise for morning workflow
2. Focus on actionable catalysts
3. Link sector moves to macro drivers
4. Flag unusual options activity
5. Note key data/speech events for session