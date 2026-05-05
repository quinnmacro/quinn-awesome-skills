# 🚢 Strait of Hormuz Transit Analysis

**Tanker Flow Monitoring & Energy Market Impact Assessment**

---

## Transit Data | 过境数据

### 24-Hour Summary

| Metric | Value | vs. 30-Day Avg | Signal |
|:-------|:------|:---------------|:-------|
| **Total Transits** | `{Transit_24h}` | `{vs_Avg_Transit}%` | `{Signal_Transit}` |
| **Crude Tankers** | `{Crude_Count}` | `{vs_Avg_Crude}%` | `{Signal_Crude}` |
| **Product Tankers** | `{Product_Count}` | `{vs_Avg_Product}%` | `{Signal_Product}` |
| **Estimated Flow** | `{Flow_Mbbl}M bbl/d` | `{vs_Avg_Flow}%` | `{Signal_Flow}` |

### Vessel Type Breakdown

| Type | Count | Avg Size | Capacity Share |
|:-----|:------|:---------|:---------------|
| **VLCC** | `{VLCC_Count}` | 300K bbl | `{VLCC_Share}%` |
| **Suezmax** | `{Suez_Count}` | 150K bbl | `{Suez_Share}%` |
| **Aframax** | `{Afra_Count}` | 80K bbl | `{Afra_Share}%` |
| **Product** | `{Prod_Count}` | 50K bbl | `{Prod_Share}%` |

---

## Queue Analysis | 队列分析

| Metric | Current | Normal Range | Status |
|:-------|:--------|:-------------|:-------|
| **Vessels Waiting** | `{Queue_Count}` | 3-8 | `{Queue_Status}` |
| **Avg Wait Time** | `{Wait_Hours}h` | 2-6h | `{Wait_Status}` |
| **Entry Speed** | `{Avg_Speed} kn` | 10-14 kn | `{Speed_Status}` |

---

## Flag Distribution | 船旗分布

| Flag | Share | Change (7d) | Risk Note |
|:-----|:------|:------------|:----------|
| **Panama** | `{Panama}%` | `{Panama_Change}` | Standard |
| **Marshall Is.** | `{Marshall}%` | `{Marshall_Change}` | Standard |
| **Liberia** | `{Liberia}%` | `{Liberia_Change}` | Standard |
| **Iran** | `{Iran}%` | `{Iran_Change}` | `{Iran_Risk}` |
| **China** | `{China}%` | `{China_Change}` | `{China_Risk}` |
| **Others** | `{Others}%` | — | — |

---

## Geopolitical Context | 地缘背景

### Recent Events (7d)

```
{Geopolitical_Events}
- List any relevant incidents
- Military activity mentions
- Political statements affecting transit
```

### Risk Indicators

| Indicator | Status | Trend |
|:----------|:-------|:------|
| **Naval Activity** | `{Naval_Status}` | `{Naval_Trend}` |
| **Political Rhetoric** | `{Rhetoric_Status}` | `{Rhetoric_Trend}` |
| **Sanctions Impact** | `{Sanctions_Status}` | `{Sanctions_Trend}` |
| **Insurance Premiums** | `{Insurance_Status}` | `{Insurance_Trend}` |

---

## Market Correlation | 市场关联

### Price Impact Analysis

| Asset | Price | Change | Transit Correlation |
|:------|:------|:------:|:--------------------|
| **WTI (CL1)** | `{WTI_Price}` | `{WTI_Change}%` | `{WTI_Corr}` |
| **Brent (CO1)** | `{Brent_Price}` | `{Brent_Change}%` | `{Brent_Corr}` |
| **OVX Vol** | `{OVX_Level}` | `{OVX_Change}%` | `{OVX_Corr}` |
| **Gasoline (XB1)** | `{XB_Price}` | `{XB_Change}%` | `{XB_Corr}` |

### Curve Implications

```
{Curve_Analysis}
- Front-month vs. 6M spread
- Calendar spread reaction
- Time spread pressure from flow disruption
```

---

## Historical Comparison | 历史对比

### Flow Benchmarks

| Period | Avg Flow | Current vs. | Event Context |
|:-------|:---------|:------------|:--------------|
| **30-Day Avg** | `{Avg_30d}M bbl/d` | `{vs_30d}%` | Normal baseline |
| **90-Day Avg** | `{Avg_90d}M bbl/d` | `{vs_90d}%` | Seasonal adjusted |
| **2019 Peak** | 22.5M bbl/d | `{vs_2019}%` | Pre-pandemic |
| **2020 Low** | 15.2M bbl/d | `{vs_2020}%` | COVID disruption |

---

## Outlook & Trading Implications | 展望与交易影响

### Immediate (1-3d)

```
{Immediate_Outlook}
- Flow trajectory
- Queue development
- Price direction bias
```

### Medium-Term (1-4w)

```
{Medium_Outlook}
- Seasonal demand patterns
- OPEC+ production alignment
- Geopolitical risk premium
```

### Trading Ideas

```
{Trading_Ideas}
- Calendar spread opportunities
- Volatility positioning
- Cross-asset correlations (energy → FX)
```

---

## Data Sources | 数据来源

```
Primary: MarineTraffic AIS data (real-time)
Secondary: Bloomberg Terminal (CL1, OVX, etc.)
Historical: TankerTrackers, EIA, OPEC
```

---

## Key Tickers | 关键Ticker

```
CL1 Comdty     # WTI Crude Front Month
CO1 Comdty     # Brent Crude Front Month
OVX Index      # Crude Oil Volatility Index
XB1 Comdty     # RBOB Gasoline Front Month
HO1 Comdty     # Heating Oil Front Month
```

---

<div align="center">

**Report Date: {Date} | Data Freshness: {Data_Age}h**

*Use with Bloomberg Terminal {AKSB <GO>} for enhanced analysis*

</div>