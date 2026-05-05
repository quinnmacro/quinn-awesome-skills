#!/usr/bin/env python3
"""Hormuz Flow Analysis & Briefing Generator."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

CACHE_DIR = Path.home() / ".cache" / "hormuz-monitor"
CACHE_FILE = CACHE_DIR / "latest.json"

BASELINES = {
    "transits_24h_avg": 18.5,
    "flow_avg_mbd": 19.0,
    "queue_normal_range": (3, 8),
}

MARKET_IMPACT = {
    "low_flow": {"wti": "+2-5%", "ovx": "+10-15%", "spread": "backwardation"},
    "normal_flow": {"wti": "neutral", "ovx": "stable", "spread": "contango"},
    "high_flow": {"wti": "-1-3%", "ovx": "-5%", "spread": "weak contango"},
}


def normalize_cached_data(payload: Any) -> dict[str, Any]:
    """Coerce cached data into the schema expected by the analyzer."""
    if not isinstance(payload, dict):
        return {}

    normalized = dict(payload)
    normalized["vessels"] = normalized.get("vessels", {})
    normalized["queue"] = normalized.get("queue", {})
    normalized["flags"] = normalized.get("flags", {})
    normalized["risk_signals"] = normalized.get("risk_signals", {})
    normalized.setdefault("timestamp", datetime.now().isoformat())
    normalized.setdefault("transits_24h", 0)
    normalized.setdefault("transits_7d_avg", BASELINES["transits_24h_avg"])
    normalized.setdefault("flow_estimate_mbd", 0.0)
    normalized.setdefault("avg_speed_kn", 0.0)
    return normalized


def load_cached_data() -> dict[str, Any]:
    """Load cached transit data."""
    if not CACHE_FILE.exists():
        print("No cached data. Run hormuz-tracker.sh first.")
        return {}

    try:
        with open(CACHE_FILE, encoding="utf-8-sig") as handle:
            return normalize_cached_data(json.load(handle))
    except (json.JSONDecodeError, OSError):
        print("Cached data is unreadable. Re-run hormuz-tracker.sh first.")
        return {}


def calculate_signals(data: dict[str, Any]) -> dict[str, str]:
    """Calculate status signals based on data."""
    signals: dict[str, str] = {}

    transits = float(data.get("transits_24h", 0))
    avg = BASELINES["transits_24h_avg"]
    deviation = (transits - avg) / avg * 100 if avg else 0.0
    if deviation < -15:
        signals["transit"] = "LOW - Disruption Risk"
    elif deviation > 10:
        signals["transit"] = "HIGH - Elevated Flow"
    else:
        signals["transit"] = "NORMAL"

    flow = float(data.get("flow_estimate_mbd", 0))
    flow_avg = BASELINES["flow_avg_mbd"]
    flow_dev = (flow - flow_avg) / flow_avg * 100 if flow_avg else 0.0
    if flow_dev < -10:
        signals["flow"] = "BELOW NORMAL"
    elif flow_dev > 5:
        signals["flow"] = "ABOVE NORMAL"
    else:
        signals["flow"] = "NORMAL"

    queue = data.get("queue", {})
    queue_count = int(queue.get("count", 0) or 0)
    low, high = BASELINES["queue_normal_range"]
    if queue_count > high:
        signals["queue"] = "ELEVATED"
    elif queue_count < low:
        signals["queue"] = "LOW"
    else:
        signals["queue"] = "NORMAL"

    return signals


def parse_timestamp(value: Any) -> datetime:
    if not isinstance(value, str):
        return datetime.now()
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return datetime.now()


def generate_briefing(data: dict[str, Any]) -> str:
    """Generate a full daily briefing."""
    if not data:
        return "No data available. Run hormuz-tracker.sh --all first."

    signals = calculate_signals(data)
    timestamp = parse_timestamp(data.get("timestamp"))
    now = datetime.now(timestamp.tzinfo)

    transits = float(data.get("transits_24h", 0))
    avg = BASELINES["transits_24h_avg"]
    vs_avg = round((transits - avg) / avg * 100, 1) if avg else 0.0

    vessels = data.get("vessels", {})
    vlcc = int(vessels.get("vlcc", 0) or 0)
    suez = int(vessels.get("suezmax", 0) or 0)
    afra = int(vessels.get("aframax", 0) or 0)
    prod = int(vessels.get("product", 0) or 0)
    total_tankers = vlcc + suez + afra
    vlcc_share = round(vlcc / max(total_tankers, 1) * 100, 1) if total_tankers else 0.0

    flow = float(data.get("flow_estimate_mbd", 0))
    flow_avg = BASELINES["flow_avg_mbd"]
    flow_vs = round((flow - flow_avg) / flow_avg * 100, 1) if flow_avg else 0.0

    queue = data.get("queue", {})
    queue_count = int(queue.get("count", 0) or 0)
    wait_hours = float(queue.get("avg_wait_hours", 0) or 0)

    flags = data.get("flags", {})
    risk = data.get("risk_signals", {})

    if flow_vs < -10:
        impact = MARKET_IMPACT["low_flow"]
        impact_note = "Potential supply disruption - upward price pressure"
    elif flow_vs > 5:
        impact = MARKET_IMPACT["high_flow"]
        impact_note = "Elevated flows - downward price bias"
    else:
        impact = MARKET_IMPACT["normal_flow"]
        impact_note = "Normal flows - neutral market"

    age_hours = int(max((now - timestamp).total_seconds(), 0) // 3600)

    return f"""
HORMUZ DAILY BRIEFING | {timestamp.strftime('%Y-%m-%d %H:%M')} UTC

TRANSIT SUMMARY
----------------------------------------
Vessels (24h):     {int(transits)} vs. avg {avg} ({vs_avg:+.1f}%)
Signal:            {signals['transit']}
Crude Flow:        ~{flow}M bbl/day ({flow_vs:+.1f}% vs avg)
Tankers Waiting:   {queue_count} ({signals['queue']})
Avg Wait:          {wait_hours}h

VESSEL BREAKDOWN
----------------------------------------
VLCC:              {vlcc} ({vlcc_share}% of crude tankers)
Suezmax:           {suez}
Aframax:           {afra}
Product Tankers:   {prod}

FLAG DISTRIBUTION
----------------------------------------
Panama:            {flags.get('panama', 0)}%
Marshall Islands:  {flags.get('marshall', 0)}%
Liberia:           {flags.get('liberia', 0)}%
Iran:              {flags.get('iran', 0)}%
China:             {flags.get('china', 0)}%
Others:            {flags.get('others', 0)}%

RISK SIGNALS
----------------------------------------
Naval Activity:    {risk.get('naval_activity', 'N/A')}
Political Rhetoric:{risk.get('political_rhetoric', 'N/A')}
Insurance Premiums:{risk.get('insurance_premiums', 'N/A')}
Queue Depth:       {signals['queue']}

MARKET IMPACT
----------------------------------------
{impact_note}
Expected WTI:      {impact['wti']}
OVX Direction:     {impact['ovx']}
Curve Shape:       {impact['spread']}

TRADING NOTES
----------------------------------------
- Monitor OVX for volatility positioning
- Watch CL1-CL6 spread for curve dynamics
- Correlate with Brent (CO1) for global context
- Cross-asset: USD strength if supply disruption

DATA SOURCES
----------------------------------------
Primary: MarineTraffic AIS (real-time)
Bloomberg: CL1, OVX, XB1, HO1 tickers
Age: {age_hours}h
""".strip()


def generate_summary(data: dict[str, Any]) -> str:
    """Generate a compact summary for Bloomberg copy-paste."""
    if not data:
        return "No data"

    transits = int(float(data.get("transits_24h", 0)))
    flow = float(data.get("flow_estimate_mbd", 0))
    queue = int(data.get("queue", {}).get("count", 0) or 0)
    signals = calculate_signals(data)
    timestamp = datetime.now().strftime("%Y-%m-%d")
    return f"{timestamp} | Hormuz: {transits} transits, {flow}M bbl/d, queue {queue}\nSignal: {signals['transit']}"


def generate_bloomberg_vars(data: dict[str, Any]) -> str:
    """Generate variable values for the Bloomberg template."""
    if not data:
        return "Run hormuz-tracker.sh --all first"

    transits = int(float(data.get("transits_24h", 0)))
    avg = BASELINES["transits_24h_avg"]
    vs_avg = round((transits - avg) / avg * 100, 1) if avg else 0.0
    vessels = data.get("vessels", {})
    queue = data.get("queue", {})
    flags = data.get("flags", {})
    total_crude = int(vessels.get("vlcc", 0) or 0) + int(vessels.get("suezmax", 0) or 0) + int(vessels.get("aframax", 0) or 0)
    vlcc_share = round(int(vessels.get("vlcc", 0) or 0) / max(total_crude, 1) * 100, 1) if total_crude else 0.0
    signals = calculate_signals(data)

    return f"""
BLOOMBERG TEMPLATE VARIABLES
----------------------------------------
{{Date}} -> {datetime.now().strftime('%Y-%m-%d')}
{{Transit_24h}} -> {transits}
{{vs_Avg_Transit}} -> {vs_avg:+.1f}
{{Signal_Transit}} -> {signals['transit']}

{{Flow_Mbbl}} -> {data.get('flow_estimate_mbd', 0)}
{{Queue_Count}} -> {queue.get('count', 0)}
{{Queue_Status}} -> {signals['queue']}
{{Wait_Hours}} -> {queue.get('avg_wait_hours', 0)}

{{VLCC_Count}} -> {vessels.get('vlcc', 0)}
{{Suez_Count}} -> {vessels.get('suezmax', 0)}
{{Afra_Count}} -> {vessels.get('aframax', 0)}
{{Prod_Count}} -> {vessels.get('product', 0)}
{{VLCC_Share}} -> {vlcc_share}

{{Panama}} -> {flags.get('panama', 0)}
{{Marshall}} -> {flags.get('marshall', 0)}
{{Liberia}} -> {flags.get('liberia', 0)}
{{Iran}} -> {flags.get('iran', 0)}

Copy these values to template.md in Bloomberg Terminal AKSB <GO>
""".strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Hormuz Flow Analysis")
    parser.add_argument("--briefing", action="store_true", help="Generate full daily briefing")
    parser.add_argument("--summary", action="store_true", help="Generate compact summary")
    parser.add_argument("--vars", action="store_true", help="Generate Bloomberg template variables")
    parser.add_argument("--signals", action="store_true", help="Calculate risk signals only")
    parser.add_argument("--save", action="store_true", help="Save briefing to file")
    args = parser.parse_args()

    data = load_cached_data()

    if args.briefing:
        output = generate_briefing(data)
        print(output)
        if args.save:
            output_file = CACHE_DIR / f"briefing_{datetime.now().strftime('%Y%m%d')}.txt"
            with open(output_file, "w", encoding="utf-8") as handle:
                handle.write(output)
            print(f"\nSaved to: {output_file}")
    elif args.summary:
        print(generate_summary(data))
    elif args.vars:
        print(generate_bloomberg_vars(data))
    elif args.signals:
        signals = calculate_signals(data)
        print("RISK SIGNALS")
        print("----------------------------------------")
        for key, value in signals.items():
            print(f"{key.upper()}: {value}")
    else:
        print(generate_briefing(data))


if __name__ == "__main__":
    main()
