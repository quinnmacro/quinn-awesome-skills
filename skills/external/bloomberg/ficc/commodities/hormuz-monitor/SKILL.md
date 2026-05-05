---
name: hormuz-monitor
description: |
  Monitor Strait of Hormuz ship flows for energy market analysis.
  Tracks tanker traffic, crude oil flows, and geopolitical risk signals.
  Triggers: "Hormuz ships", "Strait of Hormuz", "tanker flows", "oil transit",
  "Persian Gulf shipping", "energy chokepoint", "Hormuz monitor"
version: 1.0.0
author: quinnmacro
---

# Hormuz Ship Flow Monitor

Track tanker traffic through the Strait of Hormuz and convert provider payloads into a stable cache schema for Bloomberg-style energy briefings.

## Purpose

Use this skill when you need to:
- monitor a critical oil transit chokepoint
- translate vessel / transit payloads into a readable market summary
- connect shipping disruptions to crude, vol, and curve implications

## Workflow

### Step 1: Fetch data

```bash
# Current vessel positions in the Hormuz polygon
bash scripts/hormuz-tracker.sh --positions

# Transit statistics for a supported window
bash scripts/hormuz-tracker.sh --transit --period 24h
bash scripts/hormuz-tracker.sh --transit --period 7d
bash scripts/hormuz-tracker.sh --transit --period=30d

# Type breakdown and queue view
bash scripts/hormuz-tracker.sh --types
bash scripts/hormuz-tracker.sh --queue
```

### Step 2: Inspect caches

`hormuz-tracker.sh` writes two cache files under `~/.cache/hormuz-monitor/`:
- `latest.raw.json`: the raw provider payload
- `latest.json`: the normalized schema consumed by downstream analysis

Useful commands:

```bash
bash scripts/hormuz-tracker.sh --cache
bash scripts/hormuz-tracker.sh --raw-cache
```

### Step 3: Generate briefing output

```bash
python scripts/hormuz-analysis.py --briefing
python scripts/hormuz-analysis.py --summary
python scripts/hormuz-analysis.py --vars
```

## Normalized schema

Downstream tools expect `latest.json` to contain these keys:
- `timestamp`
- `transits_24h`
- `transits_7d_avg`
- `vessels.vlcc|suezmax|aframax|product`
- `flow_estimate_mbd`
- `queue.count`
- `queue.avg_wait_hours`
- `flags.panama|marshall|liberia|iran|china|others`
- `avg_speed_kn`
- `risk_signals.*`

If the live API returns a different JSON shape, `scripts/hormuz-normalize.py` converts the raw payload into this schema before the cache is overwritten.

## Data sources

Primary:
- MarineTraffic vessel / transit payloads

Secondary:
- Bloomberg Terminal (`CL1`, `OVX`, `XB1`, `HO1`)

Backup:
- TankerTrackers
- OPEC monthly reports
- EIA weekly petroleum status

## API notes

MarineTraffic response formats vary by API product tier and endpoint family. Do not assume a single raw JSON shape is stable across plans. This skill keeps the raw payload and only reads from the normalized cache for analysis.

## Configuration

```bash
export MARINETRAFFIC_API_KEY="your_key"
export BLOOMBERG_TERMINAL="enabled"
```

Optional API-shape controls:

```bash
# Official MarineTraffic examples often use path-style URLs and msgtype-gated fields.
export MARINETRAFFIC_URL_STYLE="path"      # or "query"
export MARINETRAFFIC_PROTOCOL="json"
export MARINETRAFFIC_MSGTYPE="extended"
```

## Polygon

```text
NW: 26.75N, 56.50E
NE: 26.75N, 57.00E
SW: 25.50N, 56.50E
SE: 25.50N, 57.00E
```
