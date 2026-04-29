GOAL
Produce an energy futures analysis for {Commodity} with curve structure analysis, time spread dynamics, and fundamental drivers.

TONE
Commodity trader — curve-focused, inventory-aware, basis-driven.

HEADINGS STYLE
Bold

STRUCTURE
1. Save as [{Commodity} Futures Analysis].
2. Insert today's date and current time.
3. Present futures curve as primary visualization.
4. Include time spreads and fundamental metrics.

ANALYSIS FRAMEWORK

CURVE STRUCTURE

| Contract | Price | vs Spot | Curve Position |
|----------|-------|---------|----------------|
| Spot/Front Month (M1) | [value] | - | Reference |
| M2 | [value] | [+/-] | [contango/backwardation] |
| M3 | [value] | [+/-] | [contango/backwardation] |
| M6 | [value] | [+/-] | [contango/backwardation] |
| M12 | [value] | [+/-] | [contango/backwardation] |

Calculate:
- Curve Shape: Contango (M2 > M1) or Backwardation (M1 > M2)
- Full Curve Slope: M1-M12 spread
- Mid-Curve Slope: M3-M6 spread

TIME SPREAD DYNAMICS

| Spread | Current (bp) | MTD Chg | YTD Chg | Interpretation |
|--------|--------------|---------|---------|----------------|
| M1-M2 | [value] | [value] | [value] | Front tightness |
| M2-M3 | [value] | [value] | [value] | Roll dynamics |
| M1-M3 | [value] | [value] | [value] | Near-term curve |
| M1-M6 | [value] | [value] | [value] | 6M storage arb |
| M1-M12 | [value] | [value] | [value] | Full year arb |

Comment on:
- Is spread widening/tightening?
- Storage arbitrage economics positive?
- Roll cost for long positions

PRICE PERFORMANCE

| Metric | Value | Context |
|--------|-------|---------|
| Spot Price | [value] | Current front month |
| MTD Change | [%] | Month performance |
| YTD Change | [%] | Year performance |
| 52W High | [value] | - |
| 52W Low | [value] | - |
| 52W Range Position | [%] | Where in annual range |

VOLATILITY ANALYSIS

| Metric | Value | Interpretation |
|--------|-------|----------------|
| OVX (Oil Vol Index) | [value] | Implied vol of oil options |
| 30D Realized Vol | [%] | Historical price vol |
| Vol Risk Premium | [bp] | OVX - Realized (option overpricing) |
| 3M Implied Vol | [%] | Longer-dated option pricing |
| Vol Term Structure | [shape] | Contango/backwardation of vol curve |

Comment on:
- Is implied vol elevated vs history?
- Option pricing: cheap or expensive wings?
- Vol regime: calm, elevated, crisis level

REALIZED VOL BREAKDOWN (30D)

| Metric | Value | Context |
|--------|-------|---------|
| Daily Avg Move | [+/- $/bbl] | Average intraday range |
| Max Daily Move | [+/- $/bbl] | Largest single-day swing |
| Up Days vs Down Days | [ratio] | Directional bias |
| VaR (95%, 1D) | [$/bbl] | Statistical risk estimate |

Comment on:
- Recent vol spike or calm period
- Directional trend (skewed up or down)
- Risk for position sizing

FUNDAMENTAL DRIVERS

**Inventory Data**

| Metric | Current | W/W Chg | Y/Y Chg | vs 5Y Avg |
|--------|---------|---------|---------|-----------|
| Commercial Stocks | [mb] | [value] | [value] | [+/- %] |
| Strategic Reserve | [mb] | [value] | [value] | - |
| Days of Supply | [days] | [value] | [value] | [+/- days] |

Comment on:
- Is inventory above/below seasonal norm?
- Days of supply vs comfort level

**Supply/Demand Signals**

| Factor | Status | Impact |
|--------|--------|--------|
| OPEC+ Production | [level] | [supply impact] |
| US Rig Count | [count] | [US supply trend] |
| Refinery Utilization | [%] | [demand indicator] |
| Demand Growth Forecast | [%] | [IEA/OPEC estimate] |

CRACK SPREAD & RELATED PRODUCTS

| Product | Price | vs Crude | Crack Spread |
|---------|-------|----------|--------------|
| RBOB Gasoline | [value] | [+/-] | [gasoline crack] |
| Heating Oil/Diesel | [value] | [+/-] | [distillate crack] |
| Jet Fuel | [value] | [+/-] | [jet crack] |

Calculate:
- 3:2:1 Crack Spread (3 crude : 2 gasoline : 1 distillate)
- Comment on refinery margin environment

KEY TAKEAWAYS

3-5 bullet points:
- Curve structure implication (storage play, roll cost)
- Time spread trend and arb opportunity
- Volatility regime (OVX level, vol risk premium)
- Inventory vs seasonal norm
- Supply/demand balance
- Crack spread and downstream margin

SOURCE CITATIONS RULES

Every data point must cite source:
- "Bloomberg DAPI via [ticker]"
- "EIA via Bloomberg"
- "OPEC via Bloomberg NEWS"

DATA RETRIEVAL METHOD

**Futures Prices**
```
# WTI Crude
BDP("CL1 Comdty", "PX_LAST")                # Front month
BDP("CL2 Comdty", "PX_LAST")                # M2
BDP("CL3 Comdty", "PX_LAST")                # M3
BDP("CL6 Comdty", "PX_LAST")                # M6
BDP("CL12 Comdty", "PX_LAST")               # M12

# Brent Crude
BDP("CO1 Comdty", "PX_LAST")                # Front month
# Same pattern for CO2, CO3, CO6, CO12
```

**Inventory Data (US)**
```
# EIA data via Bloomberg
DOEWCADS Index      # Commercial crude stocks
DOEWCDOS Index      # Days of supply
```

**Crack Spreads**
```
# Crack spread indices
321CRACK Index      # 3:2:1 crack spread
```

**Volatility Data**
```
BDP("OVX Index", "PX_LAST")                # CBOE Oil Volatility Index
# Or query CL option vol via VCUB
# Realized vol: calculate from daily returns or use VOLATILITY_30D field
```

TICKER MAPPING

| Commodity | Front Month | M2 | M6 | M12 | Vol Index |
|-----------|-------------|----|----|-----|-----------|
| WTI Crude | CL1 Comdty | CL2 | CL6 | CL12 | OVX Index |
| Brent Crude | CO1 Comdty | CO2 | CO6 | CO12 | OVX Index (proxy) |
| RBOB Gasoline | XB1 Comdty | XB2 | XB6 | XB12 | - |
| Heating Oil | HO1 Comdty | HO2 | HO6 | HO12 | - |
| Natural Gas | NG1 Comdty | NG2 | NG6 | NG12 | - |

TABLE REQUIREMENTS

1. Format: HTML tables
2. Prices: 2 decimals ($/bbl, $/gal)
3. Spreads: cents or $/bbl
4. Inventory: million barrels (mb)
5. Bold the M1 row

TEMPORAL PRIORITY RULES

1. TODAY: Spot, curve snapshot, intraday move
2. W/W: Inventory change, time spread shift
3. MTD: Price trend, curve evolution
4. YTD: Year performance, fundamental context

GUIDELINES

1. Always explain curve shape implication (storage/roll)
2. Link time spreads to inventory levels
3. Show crack spread for downstream context
4. Highlight seasonal inventory patterns
5. If EIA data delayed, note timing