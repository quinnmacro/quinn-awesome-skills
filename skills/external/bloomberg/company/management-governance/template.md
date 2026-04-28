# Management & Governance Study

## Metadata

| 字段 | 值 |
|------|---|
| Type | Company |
| Source | Bloomberg Official |
| Variables | `{Company Name/Ticker}`, `N` (default: 4) |
| Data Periods | N annual periods |
| Output | Management quality + governance assessment |

## Prompt Template

GOAL
Produce a concise, numerical, analytical report evaluating {Company Name/Ticker} from a management and governance lens to assess management quality, governance structure, and risk areas.

TONE
Neutral, comparative language.

TYPOGRAPHY
Use Bold for all section headings.

==================== USER INPUTS ====================
Company Name: {Company Name/Ticker}
Length of Executive Summary: 150 words
N [Number of Annual Periods] = 4

==================== ANALYSIS FRAMEWORK ====================

Governance Assessment Principle
- Evaluate:
  A) Structure (board, ownership, governance rules)
  B) Incentives (compensation alignment)
  C) Outcomes (capital allocation, performance linkage)

- Identify:
  - Alignment vs misalignment
  - Stability vs churn
  - Shareholder vs management bias

==================== TEMPORAL LOGIC ====================
A) Insert today's date and current time
B) Use latest reported fiscal periods for financial data; latest available filings for governance and compensation data
C) Always specify fiscal period or disclosure date
D) Ensure alignment between compensation periods and performance periods
E) Outdated data moves to Historical section
F) Do NOT infer newer data or assume timing if not disclosed (mark UNVERIFIED)

==================== DATA PRIORITIZATION ====================
Priority 0 (DEFAULT - Always Include):
- Data < 366 days old, current fiscal quarter/year, latest governance disclosures, recent executive changes, active compensation structures

==================== SOURCE ATTRIBUTION RULE ====================
A) Every factual claim and numerical datapoint must include a Bloomberg source citation line
B) Citation must identify source type (Company filings via Bloomberg, Bloomberg Intelligence, Bloomberg News)

==================== CONSENSUS STANDARD ====================
A) All consensus numbers must be sourced via Bloomberg Consensus

============== OUTPUT REQUIREMENTS & SEQUENCE ==============
1. Timestamp
2. [Company Name]  Management and Governance Study 
3. Table of Content
3. Executive Summary
4. Top 5 Signals on Management & Governance
------------------------------------------------------
5. Analysis Framework Summaries 

For each section:
- Headline
- Summary (<=30 words)
- Must include comparative assessment, time reference, evidence-based observation

Sections:
1) Company Overview
2) Leadership & Governance Structure
3) Market & Financial Snapshot 
4) A Chart Showing Stock Price Change under current CEO, show CEO's start date on the chart
5) A Tabular Table Showing Stock Price Performance under current CEO, accounting for the CEO's start date and compare against the SPX 500 Index performance
6) Executive Compensation Structure (annual, multi-year)
7) Shareholder Structure & Board Oversight
8) Workforce, Pension & Legal Risk
------------------------------------------------------

6. Historical Performance

Tables:
- P&L Metrics for 4 Annual Periods (when available) and y/y growth rates (%) and margin trends in bps. 
- Extract N+1 period data to ensure trend data is rendered for all rendered periods.

7. Coverage checklist

==================== METRIC FREQUENCY RULE ====================
- Compensation / Governance: Annual (multi-year trends)
- CEO Stock Performance: Full tenure period, annualized returns
- Workforce: Quarterly or Annual depending on disclosure
- Pension: Annual
- Ownership / Board: Point-in-time (latest)

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
