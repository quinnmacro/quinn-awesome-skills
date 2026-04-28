# Performance Tracker

## Metadata

| 字段 | 值 |
|------|---|
| Type | Company |
| Source | Bloomberg Official |
| Variables | `{Company Name/Ticker}` |
| Data Periods | N=8 quarters (requires N+5=13 quarters data) |
| Output | HTML tables with Q/Q and Y/Y growth |
| Special | Only template requiring HTML format |

## Prompt Template

GOAL
Produce a concise, numerical, analytical report enabling an analyst to evaluate {Company Name/Ticker} from a financial lens to support an investment thesis.

TONE
Neutral, comparative language. 

HEADINGS STYLE
Bold, Italic

STRUCTURE
1. Save as [Title].
2. Insert today's date and current time.
3. Use the title format: [Company Name] Performance Tracker.
4. For each factor in the analysis framework, include a summary with a headline and a cross-matrix HTML table with fiscal periods as columns.

ANALYSIS FRAMEWORK
Align all metrics, growth rates, and comparisons with the relevant industry sector.

COMPANY FUNDAMENTALS
1. Provide name, headquarters, IPO year/date, sector, reporting currency, stock exchange, and index membership.
2. Provide employee count and leadership (CEO, CFO, Head of IR, Chairman) with brief backgrounds.
3. Provide last and next earnings dates.
4. Provide stock price, market capitalization, net debt, cash, enterprise value, and short interest ratio.
5. Provide trailing twelve months (TTM) revenue, EPS, and free cash flow (FCF).
6. List acquisitions and disposals in the last 5 years.

FINANCIAL PERFORMANCE - LAST 8 REPORTED FISCAL QUARTERS (N)
1. Present revenue and revenue growth with year-over-year (Y/Y) and quarter-over-quarter (Q/Q) figures.
2. Present segment revenue and segment growth with Y/Y and Q/Q figures.
3. Present KPIs supporting revenue trends, including:
   a. Margins (gross, operating, net) with basis-point changes for deltas.
   b. EPS (GAAP and non-GAAP).
   c. Operating cash flow and free cash flow.

TABLE REQUIREMENTS
1. Table format: HTML.
2. Retrieve data for the Requested fiscal periods (N) plus 5 additional periods (N + 5) to enable quarter-over-quarter and year-over-year growth calculations.
3. Order columns chronologically with the most recent period first.
4. Use the following column structure exactly:
   Metric | Q1 | Q/Q % | Y/Y % | Q2 | Q/Q % | Y/Y % | Q3 | Q/Q % | Y/Y % | Q4 | Q/Q % | Y/Y % | Q5 | Q/Q % | Y/Y % | Q6 | Q/Q % | Y/Y %
5. For margin metrics, show basis-point changes instead of percentage growth.
6. Use "-" only when prior-period data is unavailable.

GUIDELINES
1. Ensure insights are unique and not redundant.
2. Always clearly reference the period associated with each data point (for example: trailing twelve months, fiscal year, calendar year).
3. Always check today's date and current time before forming conclusions.
4. If today's date minus the insight date exceeds 180 days, place the insight in a separate Historical Data section.


SOURCE CITATIONS RULES
Every factual claim, data-driven insight, and numerical data point must always include a source citation, either inline or immediately below the insight. Source lines should identify the underlying data provider (e.g., "Company filings via Bloomberg", "Bloomberg Research", "IDC estimates").
