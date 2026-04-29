GOAL
Produce an earnings event analysis for {Company/Ticker} covering quarterly results surprise, guidance revision, and peer comparison.

TONE
Institutional equity analyst — data-focused, consensus-aware, catalyst-driven.

HEADINGS STYLE
Bold

STRUCTURE
1. Save as [{Company/Ticker} Earnings Analysis: {Quarter} {Year}].
2. Insert earnings release date and current time.
3. Present surprise metrics as primary table.
4. Include guidance change and management commentary tone.

ANALYSIS FRAMEWORK

EARNINGS SURPRISE MATRIX

| Metric | Actual | Consensus | Surprise (%) | Surprise Direction |
|--------|--------|-----------|--------------|---------------------|
| Revenue | [$bn] | [$bn] | [%] | [beat/miss] |
| EPS | [$] | [$] | [%] | [beat/miss] |
| EBITDA | [$bn] | [$bn] | [%] | [beat/miss] |
| Operating Margin | [%] | [%] | [bp] | [beat/miss] |
| FCF | [$bn] | [$bn] | [%] | [beat/miss] |

Calculate:
- Aggregate surprise score: weighted average of key metrics
- Quality of beat: revenue + EPS vs single-metric beat

GUIDANCE REVISION ASSESSMENT

| Metric | New Guidance | Prior Guidance | Change (%) | Consensus Implied |
|--------|--------------|----------------|------------|-------------------|
| Revenue FY | [range] | [range] | [%] | [vs consensus] |
| EPS FY | [range] | [range] | [%] | [vs consensus] |
| Capex | [$bn] | [$bn] | [%] | [investment signal] |

Classify guidance tone:
- RAISE: Guidance above consensus → positive catalyst
- CONFIRM: Guidance inline → neutral
- CUT: Guidance below consensus → negative catalyst

MANAGEMENT COMMENTARY ANALYSIS

| Topic | Tone | Key Quote | Signal |
|-------|------|-----------|--------|
| Macro Outlook | [confident/cautious] | [excerpt] | [positive/negative] |
| Demand Trends | [strong/moderate/weak] | [excerpt] | [positive/negative] |
| Cost Pressure | [rising/stable/falling] | [excerpt] | [negative/neutral] |
| Strategic Initiatives | [on-track/delayed] | [excerpt] | [positive/negative] |

Sentiment score:
- Count positive vs negative signals
- Flag any abrupt tone change vs prior quarter

PEER REACTION & COMPARISON

| Peer | EPS Surprise (%) | Stock Reaction (%) | Sector Signal |
|------|------------------|--------------------|---------------|
| {Peer 1} | [%] | [%] | [aligned/diverged] |
| {Peer 2} | [%] | [%] | [aligned/diverged] |
| {Peer 3} | [%] | [%] | [aligned/diverged] |

Comment on:
- Sector-wide trend vs company-specific outcome
- Relative performance within peer group

STOCK REACTION ANALYSIS

| Timeframe | Price Change (%) | Volume vs Avg | Options Flow |
|-----------|------------------|---------------|--------------|
| Pre-market | [%] | [x normal] | [call/put bias] |
| Intraday | [%] | [x normal] | [call/put bias] |
| After-hours | [%] | [x normal] | [call/put bias] |

Assess:
- Initial reaction vs sustained move
- Volume confirmation of trend
- Options market positioning

KEY TAKEAWAYS

3-5 bullet points:
- Surprise quality (broad beat vs narrow beat)
- Guidance catalyst strength
- Management tone shift
- Peer comparison takeaway
- Stock reaction interpretation

SOURCE CITATIONS RULES

Every data point must cite source:
- "Bloomberg EARN via [ticker]"
- "Company press release via Bloomberg News"
- "Consensus via Bloomberg Estimates"

DATA RETRIEVAL METHOD

**Earnings Data**
```
BDP("{Company/Ticker}", "IS_EPS")              # Actual EPS
BDP("{Company/Ticker}", "BEST_EPS")            # Consensus EPS
BDP("{Company/Ticker}", "IS_REV")              # Actual Revenue
BDP("{Company/Ticker}", "BEST_REV")            # Consensus Revenue
BDP("{Company/Ticker}", "EPS_SURPRISE_PCT")    # Surprise percentage
```

**Guidance**
```
BDP("{Company/Ticker}", "BEST_EPS_1GY")        # FY1 EPS consensus
BDP("{Company/Ticker}", "BEST_REV_1GY")        # FY1 Revenue consensus
# Use Bloomberg News for guidance range extraction
```

**Peer Comparison**
```
BQS("{Sector}") to get peer tickers
BDP for each peer's EPS_SURPRISE_PCT
```

**Options Flow**
```
OI MON function for options activity
VOL function for volume analysis
```

TABLE REQUIREMENTS

1. Format: HTML tables
2. Dollar amounts: $bn with 2 decimals
3. Percentages: 1 decimal place
4. Bold actual vs consensus columns
5. Color coding in terminal: green beat, red miss

TEMPORAL PRIORITY RULES

1. RELEASE DATE: Actual vs consensus
2. IMMEDIATE: Stock reaction (0-24h)
3. 48H: Peer reaction, analyst updates
4. 1W: Guidance revision impact

GUIDELINES

1. Focus on quality of surprise, not just direction
2. Link guidance change to stock catalyst
3. Compare management tone to prior quarter
4. Flag divergence from sector trend
5. Note if reaction seems overdone or justified