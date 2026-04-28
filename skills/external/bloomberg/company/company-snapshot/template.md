# Company Snapshot

## Metadata

| 字段 | 值 |
|------|---|
| Type | Company |
| Source | Bloomberg Official |
| Variables | `{Company Name/Ticker}`, `[Peers]` (optional) |
| Data Periods | 2 FY + 4 quarters |
| Output | Investment thesis primer |

## Prompt Template

GOAL
Produce a concise, numerical primer on {Company Name/Ticker} to support investment thesis development

TONE
Neutral, comparative, evidence-based

TYPOGRAPHY
Use Bold for all section headings

==================== USER INPUTS ====================
Company Name/Ticker: {Company Name/Ticker}
Peers (optional): [Peers] extract from {Company Name/Ticker}'s latest fiscal year annual report

==================== SOURCE RULES ====================
A) Every claim must include a citation (inline or immediately below)
B) Primary sources: Company filings, earnings transcripts, investor presentations, press releases
C) Secondary sources (Scan): Sell-side research, Bloomberg Research, Expert Networks
D) Unsourced metric → "Not Disclosed" (no estimation)
E) Tag ALL metrics: GAAP / IFRS / Non-GAAP
F) Annual filings must be within 366 days — else use latest 10-Q or 8-K


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
[Company Name] Snapshot

Table of Contents

EXECUTIVE SUMMARY
   - 300-word summary
   - 3 paragraphs
   - Cover: business model, total addressable market, competitive position, primary growth driver, key risks, future outlook and ongoing strategic initiatives, LTM key performance metrics and trends.

COMPANY OVERVIEW
   - 150-word summary
   - Cover: What the company does, total addressable market (if available), key segments, how it makes money, position in ecosystem
   - Table: Attribute | Detail
     (HQ, Listing, Fiscal Year, Reporting Std, Market Cap, Employees, Segments)

FINANCIAL PERFORMANCE
   - 150-word summary
   - Table: Key performance metrics for Latest 2 (most recent) Fiscal Years 
   - Table: Key performance metrics for the Latest (most recent) 4 Fiscal Quarter
   - Prioritize Y/Y Growth over Q/Q Growth
   - For growth calculations ALWAYS get comparable previous fiscal period data points.  For example: if requested quarters are 4, we need to gather and source 9 quarters of data and if requested fiscal years are 3, we need to get data for 4 fiscal years to calculate growth rates.
-- Render only the metrics that have growth rates. Example Rule:  if 9 quarters of data is collected show 4 quarters, if data for 4 fiscal years is collected show 3 fiscal years.


COMPETITIVE BENCHMARKING
   - 150-word summary
   - Table: Metric | Company | Peer 1 | Peer 2 | Peer 3
   - Key Financial Metrics (Only if disclosed): Example - Revenue, Rev Growth, Gross Margin, EBITDA Margin

PRODUCT & MARKET POSITION
   - 150-word summary
   - Cover: product/service offerings by segment, revenue mix by product and geography, customer segments, TAM, market share (if disclosed), pricing model, differentiation vs competitors
   - Table (optional): Product/Segment | Revenue Mix (%) | Customer Segment | Pricing Model and Dynamics

OPERATIONS & SUPPLY CHAIN 
   - 150-word summary
   - Cover: key KPIs (volume, users, retention, churn), operational leverage, macro sensitivity, supplier value chain (if relevant)

STRATEGY & OUTLOOK
   - 150-word summary
   - Cover: company growth strategy, management guidance

KEY DEVELOPMENTS (Last 12 Months)
   - 10 bullets, most recent first (no table)
   - Format: [Date] - [Event] - [Impact] - (Source)
   - Cover: Earnings, M&A, Executive changes, Product launches, Regulatory

KEY EVENTS & CATALYSTS
   - A Table in Tabular Format with three columns: Timeline | Event | Event Description (Why is it important) - max 10 words

RISKS
   - 150-word summary
   - Cover (If Applicable): Customer concentration risks,execution risks,regulatory risks, competitive risks

COVERAGE CHECKLIST

==================== TEMPORAL PRIORITY RULES ====================
A) Insert today's date and current time before generating output
B) Use latest available filings
C) Reference specific fiscal periods or disclosure dates for all data

Data Age Priority:
- Priority 0 (DEFAULT — Always Include): Data < 366 days old, current FQ/FY data, latest earnings call

Rules:
- Include Priority 0 data in all sections
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
- Use "-" only when comparator data is unavailable.
- Below every table, include:
  "Comparators used for calculations (not displayed): [list prior-quarter and YoY quarters]."
- If growth is not computable, provide a specific reason.
