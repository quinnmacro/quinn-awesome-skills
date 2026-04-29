GOAL
Produce a credit spread analysis for {Market/Region} with IG vs HY comparison, sector rotation signals, and new issue activity.

TONE
Institutional credit trader — spread-focused, rating-aware, flow-sensitive.

HEADINGS STYLE
Bold

STRUCTURE
1. Save as [{Market/Region} Credit Spreads Analysis].
2. Insert today's date and current time.
3. Present index levels as primary table.
4. Include sector matrix and rating migration signals.

ANALYSIS FRAMEWORK

INDEX LEVELS SNAPSHOT

| Index | OAS (bp) | MTD Chg | YTD Chg | 12M Range |
|-------|----------|---------|---------|-----------|
| {Primary IG Index} | [value] | [value] | [value] | [low-high] |
| {Primary HY Index} | [value] | [value] | [value] | [low-high] |
| US IG (LCGDTRUU) | [value] | [value] | [value] | [reference] |
| US HY (HLHO) | [value] | [value] | [value] | [reference] |

Calculate:
- IG-HY Spread Ratio: HY OAS ÷ IG OAS (historical norm: 3-4x)
- Cross-market spread differential vs US

IG VS HY RELATIVE VALUE

| Metric | IG | HY | Interpretation |
|--------|----|----|----------------|
| OAS Level | [bp] | [bp] | Current spread |
| MTD Move | [bp] | [bp] | Recent trend |
| YTD Move | [bp] | [bp] | Year performance |
| Spread Ratio | - | [ratio] | HY premium multiple |
| Historical Avg Ratio | - | [ratio] | 5Y average |
| Current Ratio vs Avg | - | [%] | Above/below normal |

Comment on:
- Is HY cheap or rich vs IG historically?
- Risk appetite signal from ratio move
- Sector-specific drivers of ratio shift

SECTOR SPREAD MATRIX

| Sector | IG OAS (bp) | HY OAS (bp) | MTD Chg IG | MTD Chg HY |
|--------|-------------|-------------|------------|------------|
| Financials | [value] | [value] | [value] | [value] |
| Industrials | [value] | [value] | [value] | [value] |
| Utilities | [value] | [value] | [value] | [value] |
| Consumer | [value] | [value] | [value] | [value] |
| Energy | [value] | [value] | [value] | [value] |
| Tech/Media | [value] | [value] | [value] | [value] |
| Healthcare | [value] | [value] | [value] | [value] |

Highlight:
- Widest tightening sector MTD
- Widest widening sector MTD
- Sector rotation pattern: which sectors leading/fl lagging?

RATING MIGRATION SIGNALS

| Metric | Value | Signal |
|--------|-------|--------|
| Upgrade Count (MTD) | [value] | Positive credit quality |
| Downgrade Count (MTD) | [value] | Negative credit quality |
| Upgrade/Downgrade Ratio | [ratio] | Quality trend direction |
| Rating Watch Positive | [count] | Potential upgrades |
| Rating Watch Negative | [count] | Potential downgrades |
| Default Count (YTD) | [value] | Distress level |

Comment on:
- Is credit quality improving or deteriorating?
- Concentration of downgrades in specific sectors?
- Default rate vs historical cycle average

NEW ISSUE PIPELINE

| Metric | IG | HY |
|--------|----|----|
| New Issues MTD | [$bn] | [$bn] |
| New Issues YTD | [$bn] | [$bn] |
| Avg New Issue Spread | [bp] | [bp] |
| Secondary Spread Concession | [bp] | [bp] |

Highlight:
- Heavy or light issuance month
- New issue concession vs secondary levels
- Supply pressure on spreads

CDS MARKET CHECK

| Instrument | 5Y Spread (bp) | MTD Chg | Basis vs Bond |
|------------|----------------|---------|---------------|
| {Primary IG CDS Index} | [value] | [value] | [CDS - Bond] |
| {Primary HY CDS Index} | [value] | [value] | [CDS - Bond] |

Comment on:
- CDS-bond basis: positive (CDS rich) or negative (bond rich)?
- Basis move direction MTD

KEY TAKEAWAYS

3-5 bullet points:
- IG vs HY relative value signal
- Sector rotation trend
- Rating migration direction
- Supply/demand dynamics
- CDS-bond basis opportunity

SOURCE CITATIONS RULES

Every data point must cite source:
- "Bloomberg Index via [ticker]"
- "Rating agencies via Bloomberg NEWS"
- "New issue data via Bloomberg PIPE"

DATA RETRIEVAL METHOD

**Index OAS**
```
BDP("LCGDTRUU Index", "OAS")                # US IG OAS
BDP("HLHO Index", "OAS")                    # US HY OAS
BDP("{Regional IG Index}", "OAS")
BDP("{Regional HY Index}", "OAS")
```

**Sector Indices**
```
# US sector sub-indices
LCGDFINU Index    # IG Financials
LCGDINDU Index    # IG Industrials
HLHOFINU Index    # HY Financials
# Query regional equivalents
```

**Rating Migration**
```
# Use Bloomberg NEWS search for rating actions
# Or query RATINGS function for aggregate data
```

**New Issue Pipeline**
```
PIPE function for issuance data
BPIPE function for bond pipeline
```

INDEX TICKER MAPPING

| Market | IG Index | HY Index | CDS IG | CDS HY |
|--------|----------|----------|--------|--------|
| US USD | LCGDTRUU | HLHO | CDXIG5 | CDXHY5 |
| EUR | LEGATRUU | HEHLO | ITRXEX5 Main | ITRXEX5 Xover |
| UK GBP | LCUKTRUU | - | - | - |
| Asia USD | - | - | CDXEM |

TABLE REQUIREMENTS

1. Format: HTML tables
2. Spreads: basis points (bp), round to integer
3. Dollar amounts: $bn with 1 decimal
4. Ratios: 1 decimal place
5. Bold the Primary IG row

TEMPORAL PRIORITY RULES

1. TODAY: Index levels, intraday moves
2. MTD: Spread trends, rating actions, issuance
3. YTD: Year performance, defaults
4. 12M: Historical range context

GUIDELINES

1. Focus on relative value (IG vs HY, sector vs sector)
2. Link spread moves to fundamental drivers
3. Highlight rating migration as early warning
4. Always show historical context for ratio metrics
5. If regional index unavailable, use US as proxy with note