#!/usr/bin/env python3
"""Normalize raw Hormuz API payloads into the shared cache schema."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BASELINE_TRANSITS = 18.5
BASELINE_FLOW_MBD = 19.0


def as_number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        text = value.strip().replace(",", "")
        if not text:
            return None
        try:
            return float(text)
        except ValueError:
            return None
    return None


def first_value(record: dict[str, Any], keys: list[str]) -> Any:
    for key in keys:
        if key in record and record[key] not in (None, ""):
            return record[key]
    return None


def extract_records(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if not isinstance(payload, dict):
        return []

    for key in ("data", "results", "items", "records", "vessels", "transits"):
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]

    return [payload]


def infer_category(record: dict[str, Any]) -> str | None:
    candidates = [
        str(first_value(record, ["vessel_type", "ship_type", "type", "cargo_type", "size_class"]) or "").lower(),
        str(first_value(record, ["commodity", "cargo", "description"]) or "").lower(),
    ]
    text = " ".join(candidates)

    if "vlcc" in text:
        return "vlcc"
    if "suez" in text:
        return "suezmax"
    if "afra" in text:
        return "aframax"
    if "product" in text or "clean tanker" in text:
        return "product"
    if "tanker" not in text and "crude" not in text and "oil" not in text:
        return None

    dwt = as_number(first_value(record, ["dwt", "deadweight", "deadweight_tonnage", "capacity_dwt"]))
    if dwt is not None:
        if dwt >= 200000:
            return "vlcc"
        if dwt >= 100000:
            return "suezmax"
        if dwt >= 50000:
            return "aframax"
        return "product"

    return "product"


def compute_flag_mix(records: list[dict[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for record in records:
        flag = first_value(record, ["flag", "flag_name", "country", "flag_country"])
        if isinstance(flag, str) and flag.strip():
            counts[flag.strip().lower()] += 1

    total = sum(counts.values())
    if total == 0:
        return {
            "panama": 0,
            "marshall": 0,
            "liberia": 0,
            "iran": 0,
            "china": 0,
            "others": 0,
        }

    tracked = {
        "panama": 0,
        "marshall": 0,
        "liberia": 0,
        "iran": 0,
        "china": 0,
    }

    for name, count in counts.items():
        if "marshall" in name:
            tracked["marshall"] += count
        elif name in tracked:
            tracked[name] += count
        elif name == "people's republic of china":
            tracked["china"] += count

    others = total - sum(tracked.values())
    percentages = {key: round(value / total * 100) for key, value in tracked.items()}
    percentages["others"] = round(others / total * 100)
    return percentages


def infer_queue(records: list[dict[str, Any]], payload: Any) -> tuple[int, float]:
    payload_dict = payload if isinstance(payload, dict) else {}
    explicit_count = as_number(first_value(payload_dict, ["queue_count", "count", "waiting", "vessels_waiting"]))
    explicit_wait = as_number(first_value(payload_dict, ["avg_wait_hours", "wait_hours", "avg_wait", "queue_hours"]))

    wait_samples: list[float] = []
    low_speed_count = 0
    for record in records:
        speed = as_number(first_value(record, ["speed", "sog", "avg_speed", "speed_knots"]))
        if speed is not None and speed < 1:
            low_speed_count += 1
        wait = as_number(first_value(record, ["wait_hours", "waiting_hours", "queue_hours", "avg_wait_hours"]))
        if wait is not None:
            wait_samples.append(wait)

    count = int(explicit_count) if explicit_count is not None else low_speed_count
    avg_wait = explicit_wait if explicit_wait is not None else (sum(wait_samples) / len(wait_samples) if wait_samples else 0.0)
    return count, round(avg_wait, 1)


def infer_transits(payload: Any, records: list[dict[str, Any]], mode: str) -> tuple[int, float]:
    payload_dict = payload if isinstance(payload, dict) else {}

    direct_24h = as_number(first_value(payload_dict, ["transits_24h", "count_24h", "transit_count_24h"]))
    if direct_24h is not None:
        transits_24h = int(round(direct_24h))
    else:
        generic_count = as_number(first_value(payload_dict, ["count", "transit_count", "transits", "total"]))
        if generic_count is not None:
            transits_24h = int(round(generic_count))
        else:
            transits_24h = len(records)

    avg_7d = as_number(first_value(payload_dict, ["transits_7d_avg", "avg_7d", "seven_day_average"]))
    if avg_7d is None:
        avg_7d = float(transits_24h) if mode == "transit" else BASELINE_TRANSITS

    return transits_24h, round(float(avg_7d), 1)


def infer_avg_speed(records: list[dict[str, Any]], payload: Any) -> float:
    payload_dict = payload if isinstance(payload, dict) else {}
    explicit = as_number(first_value(payload_dict, ["avg_speed_kn", "avg_speed", "speed_avg"]))
    if explicit is not None:
        return round(explicit, 1)

    speeds = []
    for record in records:
        speed = as_number(first_value(record, ["speed", "sog", "avg_speed", "speed_knots"]))
        if speed is not None:
            speeds.append(speed)
    if not speeds:
        return 0.0
    return round(sum(speeds) / len(speeds), 1)


def build_normalized(payload: Any, mode: str) -> dict[str, Any]:
    if isinstance(payload, dict) and {"transits_24h", "vessels", "queue", "flags"}.issubset(payload.keys()):
        normalized = dict(payload)
        normalized.setdefault("source", {})
        normalized["source"].update({
            "provider": normalized["source"].get("provider", "marinetraffic"),
            "mode": mode,
            "normalized_from_live_api": True,
        })
        return normalized

    records = extract_records(payload)
    vessel_counts = {"vlcc": 0, "suezmax": 0, "aframax": 0, "product": 0}
    for record in records:
        category = infer_category(record)
        if category:
            vessel_counts[category] += 1

    transits_24h, transits_7d_avg = infer_transits(payload, records, mode)
    queue_count, avg_wait_hours = infer_queue(records, payload)
    avg_speed_kn = infer_avg_speed(records, payload)
    flags = compute_flag_mix(records)

    flow_estimate_mbd = round(BASELINE_FLOW_MBD * transits_24h / BASELINE_TRANSITS, 1) if transits_24h else 0.0

    risk_signals = {
        "naval_activity": "elevated" if queue_count > 8 else "normal",
        "political_rhetoric": "watch",
        "insurance_premiums": "stable",
    }

    return {
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source": {
            "provider": "marinetraffic",
            "mode": mode,
            "normalized_from_live_api": True,
            "raw_shape": type(payload).__name__,
            "record_count": len(records),
        },
        "transits_24h": transits_24h,
        "transits_7d_avg": transits_7d_avg,
        "vessels": vessel_counts,
        "flow_estimate_mbd": flow_estimate_mbd,
        "queue": {
            "count": queue_count,
            "avg_wait_hours": avg_wait_hours,
        },
        "flags": flags,
        "avg_speed_kn": avg_speed_kn,
        "risk_signals": risk_signals,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize Hormuz API payloads")
    parser.add_argument("--mode", required=True, help="Fetch mode: positions|transit|types|queue|all")
    parser.add_argument("--input", required=True, help="Raw input JSON file")
    parser.add_argument("--output", required=True, help="Normalized output JSON file")
    args = parser.parse_args()

    raw_text = Path(args.input).read_text(encoding="utf-8-sig")
    payload = json.loads(raw_text)
    normalized = build_normalized(payload, args.mode)
    Path(args.output).write_text(json.dumps(normalized, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
