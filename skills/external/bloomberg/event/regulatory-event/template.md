GOAL
Produce a regulatory event impact analysis for {Company/Ticker} covering regulatory action, compliance cost estimate, and industry-wide implications.

TONE
Compliance-aware equity analyst — policy-focused, precedent-driven, risk-sensitive.

HEADINGS STYLE
Bold

STRUCTURE
1. Save as [{Company/Ticker} Regulatory Event Analysis].
2. Insert regulatory announcement date and current time.
3. Present regulatory action details as primary context.
4. Include compliance timeline and cost estimate.

ANALYSIS FRAMEWORK

REGULATORY ACTION SUMMARY

| Element | Detail | Source |
|---------|--------|--------|
| Regulatory Body | [FDA/SEC/DOJ/EPA/etc.] | [official source] |
| Action Type | [warning/fine/approval/denial/investigation] | [official source] |
| Date Announced | [date] | [official source] |
| Effective Date | [date] | [official source] |
| Severity Level | [low/medium/high/critical] | [analyst assessment] |

Severity Classification:
- LOW: Warning letter, minor compliance issue
- MEDIUM: Fine < $100M, remediation required
- HIGH: Fine > $100M, operational restriction
- CRITICAL: License revocation, criminal charges

DIRECT IMPACT ASSESSMENT

| Impact Category | Estimate | Confidence | Timeline |
|-----------------|----------|------------|----------|
| One-time Fine/Penalty | [$mn] | [high/med/low] | [immediate] |
| Remediation Cost | [$mn] | [high/med/low] | [N quarters] |
| Ongoing Compliance Cost | [$mn/yr] | [high/med/low] | [permanent] |
| Revenue Impact | [% or $mn] | [high/med/low] | [N quarters] |
| Margin Impact | [bp] | [high/med/low] | [N quarters] |

Calculate:
- Total cost estimate range (low-high)
- EPS impact per quarter
- Cash flow drag assessment

COMPLIANCE TIMELINE

| Phase | Action | Deadline | Status |
|-------|--------|----------|--------|
| Response Required | [submission type] | [date] | [pending/completed] |
| Remediation Plan | [specific actions] | [date] | [pending/completed] |
| Implementation | [system changes] | [date] | [pending/completed] |
| Audit/Verification | [regulatory review] | [date] | [pending/completed] |

Comment on:
- Feasibility of timeline
- Resource requirements
- Risk of missed deadline

INDUSTRY-WIDE IMPLICATIONS

| Peer | Exposure Level | Prior Actions | Stock Reaction |
|------|----------------|---------------|----------------|
| {Peer 1} | [high/med/low] | [similar case?] | [%] |
| {Peer 2} | [high/med/low] | [similar case?] | [%] |
| {Peer 3} | [high/med/low] | [similar case?] | [%] |

Assess:
- Is this company-specific or industry-wide?
- Regulatory precedent likelihood
- Sector repricing risk

PRECEDENT CASE COMPARISON

| Case | Company | Outcome | Fine | Stock Impact |
|------|---------|---------|------|--------------|
| [Prior Case 1] | [ticker] | [resolution] | [$mn] | [% over N days] |
| [Prior Case 2] | [ticker] | [resolution] | [$mn] | [% over N days] |

Similarity Assessment:
- Match severity level
- Compare regulatory body approach
- Estimate outcome probability

LEGAL & LITIGATION RISK

| Risk Factor | Probability | Potential Cost | Timeline |
|-------------|-------------|----------------|----------|
| Civil Litigation | [%] | [$mn range] | [N years] |
| Class Action | [%] | [$mn range] | [N years] |
| Criminal Charges | [%] | [$mn range] | [N years] |

Comment on:
- Legal precedent for shareholder suits
- Class action threshold
- Criminal prosecution likelihood

STOCK REACTION CONTEXT

| Metric | Current | Pre-Event | Change (%) |
|--------|---------|-----------|------------|
| Stock Price | [$] | [$] | [%] |
| Trading Volume | [x avg] | [1x avg] | [vol spike] |
| Put/Call Ratio | [ratio] | [prior] | [sentiment shift] |
| Short Interest | [%] | [%] | [change] |

Assess:
- Is reaction proportional to severity?
- Overreaction opportunity vs justified fear
- Technical support levels

KEY TAKEAWAYS

3-5 bullet points:
- Severity classification and justification
- Total cost estimate with confidence level
- Timeline risk factors
- Industry contagion assessment
- Investment opportunity or avoid signal

SOURCE CITATIONS RULES

Every data point must cite source:
- "Regulatory filing via Bloomberg News"
- "Company 8-K/press release via Bloomberg"
- "Legal precedent via Bloomberg Law"

DATA RETRIEVAL METHOD

**Company Data**
```
BDP("{Company/Ticker}", "PX_LAST")             # Current price
BDP("{Company/Ticker}", "VOLUME")              # Volume
BDP("{Company/Ticker}", "SHORT_RATIO")         # Short interest
```

**News & Regulatory**
```
NEWS function for regulatory announcements
NI {Regulator} for specific agency news
```

**Peer Comparison**
```
BQS("{Sector}") for peer list
BDP for peer stock reactions
```

TABLE REQUIREMENTS

1. Format: HTML tables
2. Dollar amounts: $mn with 1 decimal
3. Percentages: 1 decimal
4. Bold severity level and cost estimates
5. Note confidence levels explicitly

TEMPORAL PRIORITY RULES

1. ANNOUNCEMENT: Action details, immediate reaction
2. 24-48H: Peer reaction, analyst commentary
3. 1W: Compliance plan clarity
4. 1Q+: Implementation progress tracking

GUIDELINES

1. Classify severity before estimating impact
2. Use precedent cases for outcome probability
3. Distinguish one-time vs ongoing costs
4. Flag industry contagion risk
5. Note if stock reaction seems disproportionate