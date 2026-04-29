GOAL
Produce an FX market review for {Currency/Region} covering G10 pairs, EM FX, and carry trade positioning.

TONE
FX strategist — carry-aware, policy-linked, volatility-focused.

HEADINGS STYLE
Bold

STRUCTURE
1. Save as [{Region} FX Market Review].
2. Insert current date and time.
3. Present G10 snapshot as primary table.
4. Include EM FX and carry trade assessment.

ANALYSIS FRAMEWORK

G10 FX SNAPSHOT

| Pair | Spot | 1D Chg (%) | 1W Chg (%) | YTD Chg (%) | Key Driver |
|------|------|------------|------------|-------------|------------|
| EUR/USD | [value] | [%] | [%] | [%] | [rates/data] |
| USD/JPY | [value] | [%] | [%] | [%] | [BoJ/Fed] |
| GBP/USD | [value] | [%] | [%] | [%] | [UK data] |
| AUD/USD | [value] | [%] | [%] | [%] | [China/commodity] |
| USD/CAD | [value] | [%] | [%] | [%] | [oil/rates] |
| EUR/GBP | [value] | [%] | [%] | [%] | [ECB/BoE] |
| EUR/JPY | [value] | [%] | [%] | [%] | [cross] |

Comment on:
- USD strength/weakness theme
- Cross-pair divergence patterns

EM FX SNAPSHOT

| Currency | Spot | 1D Chg (%) | 1W Chg (%) | YTD Chg (%) | Risk Signal |
|----------|------|------------|------------|-------------|-------------|
| USD/CNY | [value] | [%] | [%] | [%] | [PBoC stance] |
| USD/MXN | [value] | [%] | [%] | [%] | [carry/risk] |
| USD/BRL | [value] | [%] | [%] | [%] | [Brazil risk] |
| USD/INR | [value] | [%] | [%] | [%] | [RBI policy] |
| USD/ZAR | [value] | [%] | [%] | [%] | [commodity/risk] |
| USD/TRY | [value] | [%] | [%] | [%] | [Turkey risk] |

Highlight:
- EM vs USD strength correlation
- Carry vs safe-haven flow balance

CARRY TRADE MATRIX

| Funding | Target | Carry (ann.) | 3M Vol (%) | Carry/Vol | Rating |
|---------|--------|--------------|------------|-----------|--------|
| JPY | USD | [%] | [%] | [ratio] | [★/☆] |
| EUR | AUD | [%] | [%] | [ratio] | [★/☆] |
| CHF | NZD | [%] | [%] | [ratio] | [★/☆] |
| JPY | BRL | [%] | [%] | [ratio] | [★/☆] |
| EUR | TRY | [%] | [%] | [ratio] | [★/☆] |

Calculate:
- Carry: rate differential × forward points
- Carry-to-vol ratio: annual carry ÷ 3M realized vol
- Rating: ★ (carry/vol > 0.5), ☆ (below)

Comment on:
- Best carry trade opportunity
- Risk-adjusted attractiveness
- Funding currency cheapness

CENTRAL BANK POLICY DIVERGENCE

| CB | Current Rate | Next Meeting | Market Pricing | Bias | FX Impact |
|----|--------------|--------------|----------------|------|-----------|
| Fed | [%] | [date] | [+/- bp] | [hawkish/dove] | [USD direction] |
| ECB | [%] | [date] | [+/- bp] | [hawkish/dove] | [EUR direction] |
| BoJ | [%] | [date] | [+/- bp] | [hawkish/dove] | [JPY direction] |
| BoE | [%] | [date] | [+/- bp] | [hawkish/dove] | [GBP direction] |
| RBA | [%] | [date] | [+/- bp] | [hawkish/dove] | [AUD direction] |

Comment on:
- Most hawkish vs most dovish CB
- Policy divergence driving pair
- Meeting timing asymmetry

VOLATILITY CHECK

| Pair | 1M Imp Vol (%) | 3M Imp Vol (%) | Realized 3M (%) | Vol Premium |
|------|----------------|----------------|-----------------|-------------|
| EUR/USD | [%] | [%] | [%] | [bp] |
| USD/JPY | [%] | [%] | [%] | [bp] |
| GBP/USD | [%] | [%] | [%] | [bp] |
| AUD/USD | [%] | [%] | [%] | [bp] |

Comment on:
- Vol cheap or expensive
- Hedging cost implication
- Risk reversal direction

FX CORRELATION CHECK

| Pair | Correlation | Recent Divergence | Explanation |
|------|-------------|-------------------|-------------|
| EUR/USD vs USD/JPY | [value] | [yes/no] | [risk-off flow] |
| AUD/USD vs USD/CAD | [value] | [yes/no] | [commodity split] |
| EM vs G10 | [value] | [yes/no] | [risk appetite] |

KEY TAKEAWAYS

3-5 bullet points:
- USD direction theme
- Best carry trade setup
- Policy divergence driver
- Volatility environment
- EM risk signal

SOURCE CITATIONS RULES

Every data point must cite source:
- "Bloomberg FX via [ticker]"
- "Central bank via Bloomberg"
- "Volatility via Bloomberg VCUB"

DATA RETRIEVAL METHOD

**FX Spot**
```
BDP("EURUSD Curncy", "PX_LAST")                # EUR/USD spot
BDP("USDJPY Curncy", "PX_LAST")                # USD/JPY spot
BDP("USDCNH Curncy", "PX_LAST")                # USD/CNY
```

**FX Changes**
```
BDP("EURUSD Curncy", "CHG_PCT_1D")             # 1 day change
BDP("EURUSD Curncy", "CHG_PCT_5D")             # 5 day change
BDP("EURUSD Curncy", "CHG_PCT_YTD")            # YTD change
```

**Volatility**
```
VCUB function for implied vol
BDP("{Pair}3M Curncy", "VOLATILITY_3M")        # 3M implied vol
```

**Central Bank**
```
FDTR             # Fed rate
ECBDFR           # ECB rate
BOJPOLICY        # BOJ rate
UKBRBASE         # BOE rate
RBATCTR          # RBA rate
```

TABLE REQUIREMENTS

1. Format: HTML tables
2. FX rates: 4 decimals (2 for JPY)
3. Changes: percentage 1 decimal
4. Carry/vol: ratio with 2 decimals
5. Bold G10 pairs

TEMPORAL PRIORITY RULES

1. TODAY: Spot snapshot, daily moves
2. 1W: Short-term trend
3. 3M: Volatility context
4. YTD: Year performance
5. Policy cycle: CB divergence

GUIDELINES

1. Focus on carry-to-vol as key metric
2. Link FX moves to rate differential
3. Flag correlation breakdowns
4. Highlight EM vs G10 risk signal
5. Note upcoming CB meetings