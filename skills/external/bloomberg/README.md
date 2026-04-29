<div align="center">

# 🫧 Bloomberg AI Prompts

**Professional prompt templates for Bloomberg Terminal `{AKSB <GO>}`**

*Fixed Income • Currencies • Commodities • Credit • Equities*

---

[![Bloomberg](https://img.shields.io/badge/Platform-Bloomberg_Terminal-blue?style=for-the-badge)](https://www.bloomberg.com/professional/solution/bloomberg-terminal/)
[![Templates](https://img.shields.io/badge/Templates-33-green?style=for-the-badge)]()
[![FICC](https://img.shields.io/badge/FICC-26_prompts-orange?style=for-the-badge)]()
[![Equity](https://img.shields.io/badge/Equity-7_templates-purple?style=for-the-badge)]()

</div>

---

## 📊 Quick Navigation

| Category | Templates | Description |
|:--------:|:---------:|:------------|
| [🏢 **Equity**](#-equity-prompts) | 7 | Company, Sector, Event analysis |
| [📈 **FICC**](#-ficc-prompts) | 26 | Rates, FX, Credit, Commodities |
| [⚡ **Mini Prompts**](#-mini-prompts) | 14 | Quick daily analysis |
| [🎭 **Theme Prompts**](#-theme-prompts) | 7 | Macro scenario analysis |

---

## 🏢 Equity Prompts

> **Company & Sector Analysis for Investment Decisions**

### 📋 Template Index

| Template | Perspective | Use Case | Variable |
|:---------|:-----------:|:---------|:---------|
| [Trends Analysis](company/trends-analysis/template.md) | 🏭 Company | Stock + Financial + Operational trends | `{Company/Ticker}` |
| [Management & Governance](company/management-governance/template.md) | 🏭 Company | Board & leadership assessment | `{Company/Ticker}`, `N` |
| [Company Snapshot](company/company-snapshot/template.md) | 🏭 Company | Investment thesis primer | `{Company/Ticker}` |
| [Performance Tracker](company/performance-tracker/template.md) | 🏭 Company | Quarterly financial tracking | `{Company/Ticker}`, `N` |
| [Sector Snapshot](sector/sector-snapshot/template.md) | 🏭 Sector | Industry + peer comparison | `{Sector Name}` |
| [Breaking Event](event/breaking-event/template.md) | ⚡ Event | Material event analysis (24-96h) | `{Company/Ticker}` |
| [Credit Strategy](market/credit-strategy/template.md) | 📊 Market | Credit market morning briefing | `{Market}` |

### 🎯 Usage

```
1. Bloomberg Terminal → {AKSB <GO>}
2. Copy template → Replace variables
3. Example: {Company/Ticker} → AAPL US Equity
```

<details>
<summary>📖 Variable Format Guide</summary>

| Variable | Format | Example |
|----------|--------|---------|
| `{Company/Ticker}` | Bloomberg Ticker | `AAPL US Equity`, `700 HK Equity` |
| `{Sector Name}` | Industry Name | `Technology`, `Healthcare` |
| `{Market}` | Market Type | `US IG`, `Asia HY`, `EM USD` |
| `N` | Period Count | `4`, `8` |

</details>

---

## 📈 FICC Prompts

> **Fixed Income, Currencies & Commodities Analysis**

### 🔥 Core Templates (5)

| Template | Category | Key Metrics |
|:---------|:--------:|:------------|
| [Sovereign Yields](ficc/rates/sovereign-yields/template.md) | 📉 Rates | Yield curve + CB policy pricing |
| [Currency Cross](ficc/fx/currency-cross/template.md) | 💱 FX | Spot/Forward + Carry + Vol |
| [Credit Spreads](ficc/credit/spreads/template.md) | 💳 Credit | IG vs HY + Sector matrix |
| [Energy Futures](ficc/commodities/energy-futures/template.md) | 🛢️ Commodities | Curve structure + OVX volatility |
| [Cross-Asset](ficc/cross-asset/template.md) | 🔗 Multi-Asset | Transmission chains |

### 📚 FICC Documentation

| Document | Content |
|:---------|:--------|
| [📖 Design Framework](ficc/FICC-DESIGN.md) | Strategy types + Methodology |
| [🔍 Quick Reference](ficc/QUICK-REFERENCE.md) | Ticker lookup + BQL templates |
| [💡 Trader Tips](ficc/TRADER-TIPS.md) | Pitfalls + Formulas + Jargon |
| [📋 Case Studies](ficc/CASE-STUDIES.md) | 7 real & scenario examples |

### 🎯 FICC by Strategy Type

```
📊 Rates      → Curve trades (Steepener/Flattener)
💱 FX        → Carry trades + Vol strategies  
💳 Credit    → IG/HY rotation + Sector RV
🛢️ Commodities → Calendar spreads + Crack spreads
🔗 Cross-Asset → Transmission analysis
```

---

## ⚡ Mini Prompts

> **Quick Analysis for Daily Workflow**

### 📅 Daily Workflow

| Prompt | Use When | Time |
|:-------|:---------|:----:|
| **Pre-Market Scan** | Before market open | 5 min |
| **Close Review** | End of trading day | 10 min |
| **Weekly Wrap** | Friday close | 15 min |

### ⚡ Event-Driven

| Prompt | Trigger |
|:-------|:--------|
| **Rate Decision Reaction** | CB meeting outcome |
| **Geopolitical Shock** | War, sanctions, election |
| **Data Release Reaction** | CPI, NFP, GDP surprise |

### 📊 Relative Value

| Prompt | Use Case |
|:-------|:---------|
| **Curve Trade Setup** | Steepener/Flattener ideas |
| **Credit RV** | IG vs HY relative value |
| **FX Carry Trade** | Carry attractiveness check |

### 🛡️ Risk & Stress

| Prompt | Purpose |
|:-------|:--------|
| **Market Stress Check** | Cross-asset stress level |
| **Liquidity Assessment** | Market functioning check |
| **Position Risk Check** | VaR + Stop-loss sizing |

---

## 🎭 Theme Prompts

> **Macro-Driven Scenario Analysis**

| Theme | When to Use |
|:------|:------------|
| 🌡️ **Inflation Trade** | CPI surprises, breakeven moves |
| 📉 **Recession Trade** | Curve inversion, LEI decline |
| 💧 **Liquidity Crisis** | Bid-ask widening, market freeze |
| ⚖️ **CB Divergence** | Rate differential widening |
| ❌ **Policy Mistake** | Real rates extreme |
| 📊 **Tail Risk** | Geopolitical escalation |
| 🦢 **Black Swan Prep** | Portfolio resilience check |

---

## 🗂️ Directory Structure

```
bloomberg/
│
├── 📄 README.md                    # You are here
│
├── 🏢 company/                     # Equity - Company
│   ├── trends-analysis/
│   ├── management-governance/
│   ├── company-snapshot/
│   └── performance-tracker/
│
├── 🏭 sector/                      # Equity - Sector
│   └── sector-snapshot/
│
├── ⚡ event/                       # Equity - Event
│   └── breaking-event/
│
├── 📊 market/                      # Market-wide
│   └── credit-strategy/
│
└── 📈 ficc/                        # FICC Prompts
    ├── README.md
    ├── FICC-DESIGN.md
    ├── QUICK-REFERENCE.md
    ├── MINI-PROMPTS.md
    ├── CASE-STUDIES.md
    ├── THEME-PROMPTS.md
    ├── TRADER-TIPS.md
    │
    ├── rates/sovereign-yields/
    ├── fx/currency-cross/
    ├── credit/spreads/
    ├── commodities/energy-futures/
    └── cross-asset/
```

---

## 🚀 Quick Start

### First Time

```bash
# Clone the repository
git clone https://github.com/quinnmacro/quinn-awesome-skills.git

# Navigate to Bloomberg prompts
cd quinn-awesome-skills/skills/external/bloomberg
```

### Using a Template

```bash
# 1. Open template file
cat company/trends-analysis/template.md

# 2. Copy to Bloomberg Terminal {AKSB <GO>}

# 3. Replace variables
# {Company/Ticker} → AAPL US Equity

# 4. Run analysis
```

---

## 📊 Stats

| Metric | Count |
|:-------|------:|
| Total Templates | 33 |
| FICC Prompts | 26 |
| Equity Templates | 7 |
| Case Studies | 7 |
| Documentation Pages | 11 |

---

## 📜 Template Sources

| Source | Templates |
|:-------|:---------:|
| Bloomberg Official | 6 |
| Custom (User-Written) | 1 (Credit Strategy) |

---

## 🔗 Related Resources

- [Bloomberg Terminal](https://www.bloomberg.com/professional/solution/bloomberg-terminal/)
- [Bloomberg AI Documentation](https://www.bloomberg.com/professional/solution/bloomberg-terminal/)
- [Wind Prompts](../wind/) *(Coming Soon)*

---

<div align="center">

**Made with 💙 for FICC & Equity Traders**

*Star ⭐ this repo if you find it useful!*

[⬆ Back to Top](#-bloomberg-ai-prompts)

</div>
