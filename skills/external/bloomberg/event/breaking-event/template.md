# Breaking Event Analysis

## Metadata

| 字段 | 值 |
|------|---|
| Type | Event |
| Source | Bloomberg Official |
| Variables | `{Company Name/Ticker}` |
| Time Window | 24-96 hours |
| Output | Event impact assessment |

## Prompt Template

GOAL
Produce a concise, numerical, and analytical report on a material event involving {Company Name/Ticker} that occurred within the last 24–72 hours, and assess implications.

TONE
Maintain a neutral, comparative, analytical, and evidence-based tone.

TYPOGRAPHY
Use Bold for all section headings.

==================== USER INPUTS ====================
Company Name/Ticker: {Company Name/Ticker}

==================== MATERIAL EVENTS UNIVERSE ====================
Earnings, Restructuring, M&A, executive changes, production/supply chain disruptions, product launches, CMDs/business updates/roadshows, geopolitics/labor disputes, analyst rating changes, shareholder moves, market momentum, regulatory filings.

==================== SOURCE ATTRIBUTION RULE ====================
A) Every factual claim or number must include a citation inline or immediately below.
B) Citation must identify the provider and source type where possible (for example: Company filings via Bloomberg, Bloomberg Research, company press release, earnings transcript, IDC estimates).
C) If a claim or number cannot be sourced, it must not be used in conclusions.

==================== IMPORTANT CHECK ====================
A) The material event must have occurred within the last 24–96 hours.
B) Do not use any number in conclusions if context is missing; mark it as UNVERIFIED.
C) If conflicting figures are found, mark them as DISCREPANCY and present all conflicting values with source locators.
D) Reference the specific period, as-of date, or event timestamp for every material datapoint.

==================== ANALYSIS FRAMEWORK ====================
Material Event 
- Classify event type.
- State event date/time and what changed versus prior expectations.

Business Context
- Review filings, press releases, earnings transcripts, conference transcripts, and investor presentations.
- Relevant business lines, geographies, and customer segments tied to the event.
- What was expected pre-event, prevailing narrative

Qualitative and Directional Implications:
- Key takeaways in 150 words covering potential operational, strategic positioning and financial implications from the key material event.
- 1 Table showing relevant key performance metrics data in tabular format  to support the assessment
- 1 Relevant Chart (OPTIONAL)

Strategic Implications (OPTIONAL)
- Competitive position, differentiation, pricing power, customer/partner leverage, market structure, and second-order effects.

Operational Implications (OPTIONAL)
- Execution risks and timing, dependencies, bottlenecks, capacity, labor/process impacts, integration complexity if relevant, and tracking indicators.

Market Reaction + Positioning (OPTIONAL)
- Market reaction including price, volume, and relative performance versus peers/benchmarks if available.
- What the market appears to be pricing.

Comparable Historical Events (OPTIONAL)
- Include 2–3 similar setups.
- Describe what followed in fundamentals, asset price, and time-to-normalization.
- State similarities and differences versus today.

Recent Developments (LAST 30 DAYS)
- Themes from company news, relevant sell-side commentary, and broader thematic developments.
- Highlight (if relevant) shifts in organic growth, constant-currency growth, FX, and M&A contribution.

Upcoming Catalysts (NEXT 30 DAYS)
   - A Table in Tabular Format with three columns: Timeline | Event | Event Description (Why is it important) - max 10 words

============== OUTPUT REQUIREMENTS ==============
Title: Breaking Event Analysis on [Company Name/Ticker]

Timestamp: Insert the current date and time at the start of the report.

Table of Contents

a) Executive Summary
- Maximum 150 words covering.
- what happened
- why it matters
- strategic implications
- +/- 1-day stock move relative to benchmark index related to the event 
impact on market narrative pre-event and swing factors if uncertain


  b) 3–5 numbered reasons supporting the main point, each with data evidence, directional comparison, and context.

c) Take aways from Analysis Framework
- Present all required sections in the exact order below.
- Include a section summary of maximum 50 words for each section.
- Include implications where relevant.

d) Coverage Checklist

==================== DATA STRUCTURE & CALCULATIONS ====================
Numeric Rules
- Every number must include metric, unit/currency, period or as-of date, and source locator 
- Use exact text; do not round or reformat unless clearly stated as an estimate or formatting convention.
- Cross-check units and qualifiers, including GAAP/non-GAAP and actual/guidance.
- Prioritize Y/Y Growth over Q/Q Growth
   - For growth calculations ALWAYS get comparable previous fiscal period data points.  For example: if requested quarters are 4, we need to gather and source 9 quarters of data and if requested fiscal years are 3, we need to get data for 4 fiscal years to calculate growth rates.
-- Render only the metrics that have growth rates. Example Rule:  if 9 quarters of data is collected show 4 quarters, if data for 4 fiscal years is collected show 3 fiscal years.

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

==================== TEMPORAL PRIORITY RULES ====================
Temporal Integrity
- Reference the specific period for every data point.
- If a data point or insight is more than 180 days old from today's date, move it to a Historical Data section.
