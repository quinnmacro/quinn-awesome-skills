# Sector Snapshot

## Metadata

| 字段 | 值 |
|------|---|
| Type | Sector |
| Source | Bloomberg Official |
| Variables | `{Sector Name}`, `{Focus: Company Name/Ticker}`, `{Focus: Region}`, `[Peers]` (optional) |
| Data Periods | 3 FY |
| Output | Industry + peer comparative analysis |

## Prompt Template

GOAL
Produce a concise, top-down industry and peer snapshot based solely on public company filings, investor materials, and sourced industry data. No external speculation. No unsourced derived metrics.

TONE
Neutral, comparative, evidence-based (no opinions)

TYPOGRAPHY
Use Bold for all section headings

==================== USER INPUTS ====================

Sector Name: {Sector Name}
Focus Company: {Focus: Company Name/Ticker}
Focus Region: {Focus: Region}
Peers: [Peers] (optional — extract from 10-K if not provided, minimum 3)

==================== SOURCE RULES ====================

A) Every claim must include a citation (inline or immediately below)
B) Primary sources: Company filings, earnings transcripts, investor presentations, press releases
C) Secondary sources (Scan): Sell-side research, Bloomberg Research, Expert Networks

E) Unsourced metric → "Not Disclosed" (no estimation)
F) Tag ALL metrics: GAAP / IFRS / Non-GAAP
G) Annual filings must be within 366 days — else use latest 10-Q or 8-K


==================== DATA STRUCTURE & CALCULATIONS ====================
Numeric Rules
- Do NOT compute averages/medians unless ALL inputs are sourced
- Every number must include metric, unit/currency, period or as-of date, and source locator 
- Use exact text; do not round or reformat unless clearly stated as an estimate or formatting convention.
- Cross-check units and qualifiers, including GAAP/non-GAAP and actual/guidance.
- Prioritize Y/Y Growth over Q/Q Growth
- For growth calculations ALWAYS get comparable previous fiscal period data points.  For example: if requested quarters are 4, we need to get 9 quarters of data and if requested fiscal years are 3, we need to get data for 4 fiscal years.
- ALWAYS Render quarters and annuals with growth rates. For Example: If 9 quarters of data is collected show 4 quarters, if data for 4 fiscal years is collected show 3 fiscal years.

==================== OUTPUT STRUCTURE & ANALYSIS FRAMEWORK  ====================

Timestamp: Insert current date and time
{Sector Name} Snapshot

TABLE OF CONTENTS

EXECUTIVE SUMMARY 
   - 300-word summary
   - 2-3 paragraphs
   - Top-down: industry structure → competitive dynamics → company positioning → tam

SECTOR STRUCTURE
   - 300-word summary
   - HTML table: Company | Revenue ($M) | Revenue Concentration (H/M/L)
   - Cover: key players, market concentration, entry barriers, revenue dynamics, cost dynamics, profitability dynamics

ADDRESSABLE MARKET & POSITIONING
   - 300-word summary
   - {Focus: Company Name/Ticker} | Peer 1 | Peer 2 | Peer 3 |
   - Table in tabular format: Company | Positioning | Product Overlap | Segment

FINANCIAL BENCHMARKING
   - 300-word summary
   - Table in tabular format: Metric | {Focus: Company Name/Ticker} | Peer 1 | Peer 2 | Peer 3 | Acct Std
   - Key Financial Metrics (Based On Relevance): Example Revenue, Rev Growth YoY, Gross Margin, EBITDA Margin, OpEx, Debt/EBITDA

REGULATORY AND OPERATIONAL ENVIRONMENT
   - 300-word summary
   - Table in tabular format: Factor | Description | Impact on {Focus: Company Name/Ticker} | Timing
   - Cover (Based On Relevance): regulatory oversight, compliance regimes, supply chain dynamics (upstream/downstream), demand drivers, seasonality, cyclical patterns

MARKET OUTLOOK AND RISK FACTORS
   - 300-word summary
   - Table in tabular format: Factor | Type (Tailwind/Headwind) | Magnitude | Timing | Impact on {Focus: Company Name/Ticker}
   - Cove (Based On Relevance): tailwinds/headwinds, cyclicality, macro metrics (inflation, FX, GDP correlation, interest rate sensitivity)

KEY INDUSTRY DEVELOPMENTS (Last 3 Years)
   - 10 chronological bullets (no table)
   - Format: [Date] - [Event] - [Factor Tag] - [Impact] - (Source)
   - Factor tags: Cyclicality / Pricing / Technology / Supply Chain / Geopolitics / Regulation / M&A

ANALYSTS OUTLOOK ON {Sector Name} SECTOR (Conditional)
   - Include ONLY if sell-side research available
   - 2 paragraphs (300 words max each): top 2 sell-side themes
   - If unavailable: "Limited sell-side coverage — section omitted"

KEY EVENTS & CATALYSTS
   - 50-word summary
   - A Table in Tabular Format with three columns: Timeline (latest first) | Event | Event Description (Why is it important) - max 10 words

COVERAGE CHECKLIST

==================== TEMPORAL PRIORITY RULES ====================
A) Insert today's date and current time before generating output
B) Use latest available filings
C) Reference specific fiscal periods or disclosure dates for all data

Data Age Priority:
- Priority 0 (DEFAULT — Always Include): Data < 366 days old, current FQ/FY data, latest earnings call

Rules:
- YoY must use same-period comparators only (no mixing interim and FY)

==================== TABLE STANDARDS ====================
Table Format
- All tables must be rendered in Tabular format
- Use actual fiscal period labels.
- Columns: Metric | (Fiscal Period 1) | (Fiscal Period 2) | ... up to displayed N

Row Requirements
Each metric must occupy three consecutive rows:
1) Metric
2) Year-over-Year Growth % (or bps for margins)

Formatting Rules
- Never mix absolute values and growth metrics in the same row.
- Use " " only when comparator data is unavailable.
- Below every table, include:
  "Comparators used for calculations (not displayed): [list prior-quarter and YoY quarters]."
- If growth is not computable, provide a specific reason.
