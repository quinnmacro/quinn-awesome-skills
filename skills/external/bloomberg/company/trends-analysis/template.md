# Trends Analysis

## Metadata

| 字段 | 值 |
|------|---|
| Type | Company |
| Source | Bloomberg Official |
| Variables | `{Company Name/Ticker}` |
| Data Periods | YTD + 9 quarters |
| Output | Visualization-led report |

## Prompt Template

GOAL
Deliver a clear, data-driven and visualization-led report on  {Company Name/Ticker} stock performance, financial health, and operational trends using standardized, insight-focused charts.

TONE
Neutral, comparative language. 

HEADINGS STYLE
Bold, Italic

STRUCTURE
1. Save as [Title].
2. Insert today's date and current time.
3. Use the title format: [Company Name] Trends.


ANALYSIS FRAMEWORK
1. Get today's date.
2. Based on today's date, show company year-to-date stock price performance.
3. Align all metrics, growth rates, and comparisons with the relevant industry sector.
4. Get company-specific key financial metrics by quarter for the last 9 reported fiscal quarters.
5. Get company-specific key operational metrics by quarter for the last 9 reported fiscal quarters.
6. Get Y/Y growth rates for the last 4 reported fiscal quarters for all key financial metrics.
7. Get consensus estimates for company-specific key financial metrics for next 2 upcoming fiscal quarters.
8. Get consensus estimates for company-specific key financial metrics for next 2 upcoming fiscal years.

CHART REQUIREMENTS
1. Create individual charts for each of the above key financial metrics.
2. Ensure consistent scale with two decimals like 10.50 | 11.75 | 10.00
3. Ensure clear labels for X axis and Y axis.
4. Clear chart titles
5. Each operational and financial metric chart period labels should be like:
1Q YY | 2Q YY | 3Q YY | 4Q YY
6. Do not show two metrics in a single chart.

GUIDELINES
Always provide a headline that summarizes the key finding for each chart in two lines.

SOURCE CITATIONS RULES
Every factual claim, data-driven insight, and numerical data point must always include a source citation, either inline or immediately below the insight. Source lines should identify the underlying data provider (e.g., "Company filings via Bloomberg", "Bloomberg Research", "IDC estimates").
