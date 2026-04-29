GOAL
Produce an M&A event analysis for {Company/Ticker} covering deal structure, valuation metrics, synergy estimates, and approval probability.

TONE
M&A-focused equity analyst — valuation-driven, precedent-aware, regulatory-sensitive.

HEADINGS STYLE
Bold

STRUCTURE
1. Save as [{Company/Ticker} M&A Analysis: {Target/Acquirer}].
2. Insert announcement date and current time.
3. Present deal terms as primary table.
4. Include valuation comparison and synergy assessment.

ANALYSIS FRAMEWORK

DEAL STRUCTURE SUMMARY

| Element | Detail | Note |
|---------|--------|------|
| Deal Type | [acquisition/merger/LBO/spinoff] | [strategic rationale] |
| Acquirer | {Company/Ticker} | [buyer profile] |
| Target | {Target/Ticker} | [target profile] |
| Deal Value | [$bn] | [enterprise value] |
| Consideration | [cash/stock/mixed] | [ratio if mixed] |
| Premium Paid | [%] | [over target prior close] |
| Expected Close | [date] | [timeline estimate] |

Deal Type Classification:
- STRATEGIC: Synergy-driven, long-term value
- FINANCIAL: LBO, PE acquisition, leverage focus
- MERGER OF EQUALS: Combined entity, relative valuation critical
- SPINOFF: Value unlock, sum-of-parts analysis

VALUATION METRICS

| Metric | Deal Implied | Target Standalone | Premium Analysis |
|--------|--------------|-------------------|------------------|
| EV/EBITDA | [multiple] | [multiple] | [% above normal] |
| EV/Revenue | [multiple] | [multiple] | [% above normal] |
| P/E (if public) | [multiple] | [multiple] | [% above normal] |
| EV/Synergy Value | [ratio] | - | [synergy capture] |

Calculate:
- Premium over 52-week high: [deal price - 52wk high]/52wk high
- Premium over peer average multiple
- Control premium justification

SYNERGY ANALYSIS

| Synergy Type | Target Amount | Confidence | Timeline |
|--------------|---------------|------------|----------|
| Cost Synergies | [$mn/yr] | [high/med/low] | [N years] |
| Revenue Synergies | [$mn/yr] | [high/med/low] | [N years] |
| Tax Benefits | [$mn] | [high/med/low] | [one-time/ongoing] |
| Financing Benefit | [$mn/yr] | [high/med/low] | [debt cost reduction] |

Synergy Realization Assessment:
- Cost synergies: execution risk vs historical precedent
- Revenue synergies: customer retention risk
- One-time costs to achieve synergies: [$mn]

ACQUIRER IMPACT

| Metric | Pre-Deal | Post-Deal Proforma | Impact |
|--------|----------|---------------------|--------|
| EPS | [$] | [$] | [accretion/dilution %] |
| EBITDA | [$bn] | [$bn] | [increase %] |
| Debt/EBITDA | [ratio] | [ratio] | [leverage change] |
| Credit Rating | [rating] | [rating?] | [upgrade/stable/downgrade] |

Comment on:
- EPS accretion timeline (Year 1 vs Year 3)
- Leverage comfort vs credit risk
- Proforma credit rating estimate

REGULATORY APPROVAL PROBABILITY

| Regulatory Body | Jurisdiction | Risk Level | Timeline | Prior Precedent |
|-----------------|--------------|------------|----------|-----------------|
| DOJ/FTC | US | [low/med/high] | [months] | [similar cases] |
| EU Commission | EU | [low/med/high] | [months] | [similar cases] |
| CFIUS | US (if foreign) | [low/med/high] | [months] | [national security] |
| Other | [country] | [low/med/high] | [months] | [local requirements] |

Approval Probability Assessment:
- Calculate composite approval chance
- Flag biggest regulatory hurdle
- Divestiture requirement likelihood

DEAL BREAK RISK FACTORS

| Risk Factor | Probability | Trigger | Impact on Stock |
|--------------|-------------|---------|-----------------|
| Regulatory Block | [%] | [antitrust finding] | [% target drop] |
| Financing Failure | [%] | [debt market freeze] | [% target drop] |
| Target Board Rejection | [%] | [better bid emerges] | [% target drop] |
| Material Adverse Change | [%] | [earnings miss/MAC clause] | [% target drop] |

Comment on:
- Most likely deal break scenario
- Target downside to pre-deal level
- Acquirer downside if deal breaks

ARBITRAGE SPREAD ANALYSIS (if public target)

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Current Target Price | [$] | Market pricing |
| Deal Price | [$] | Contracted value |
| Arbitrage Spread | [%] | Risk premium |
| Implied Approval Probability | [%] | From spread |
| Annualized Return if Close | [%] | Time-weighted |

Calculate:
- Implied probability from spread: (Deal - Current)/(Deal - Pre-Announcement)
- Risk/reward for merger arbitrage
- Compare to historical spread norms

KEY TAKEAWAYS

3-5 bullet points:
- Deal valuation: fair, rich, or cheap vs precedent
- Synergy achievability assessment
- Regulatory approval probability
- Acquirer accretion/dilution profile
- Arbitrage opportunity or risk

SOURCE CITATIONS RULES

Every data point must cite source:
- "Deal announcement via Bloomberg News"
- "Company filings via Bloomberg"
- "Regulatory precedent via Bloomberg Law"

DATA RETRIEVAL METHOD

**Deal Data**
```
BDP("{Target/Ticker}", "PX_LAST")              # Target price
BDP("{Acquirer/Ticker}", "PX_LAST")            # Acquirer price
BDP("{Target/Ticker}", "EV")                   # Enterprise value
BDP("{Target/Ticker}", "EBITDA")               # EBITDA
```

**News & Filings**
```
MNA function for M&A news
NEWS function for deal updates
```

**Regulatory**
```
Bloomberg Law for antitrust precedent
NI DOJ or NI FTC for regulatory news
```

TABLE REQUIREMENTS

1. Format: HTML tables
2. Dollar amounts: $bn/$mn as appropriate
3. Multiples: 1 decimal place
4. Percentages: 1 decimal
5. Bold deal value and synergy targets

TEMPORAL PRIORITY RULES

1. ANNOUNCEMENT: Deal terms, initial reaction
2. 48H: Analyst commentary, peer reaction
3. 1W: Regulatory filing clarity
4. MONTHS: Approval progress tracking
5. CLOSE: Synergy realization monitoring

GUIDELINES

1. Focus on valuation justification for premium
2. Assess synergy credibility vs management claims
3. Calculate arbitrage spread for public targets
4. Flag regulatory hurdles explicitly
5. Note accretion timeline vs investor patience