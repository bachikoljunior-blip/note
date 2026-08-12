#!/usr/bin/env python3
"""Fail closed when usage or revenue measurements are too old to call current."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_MAX_AGE_HOURS = {
    "usage": 2.0,
    "claude_usage": 2.0,
    "gumroad_sales": 3.0,
    "itch_stats": 3.0,
}


def parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError(f"timestamp has no timezone: {value}")
    return parsed.astimezone(timezone.utc)


def audit_measurements(
    sources: dict[str, dict[str, Any]], as_of: datetime
) -> dict[str, Any]:
    measurements: dict[str, Any] = {}
    stale: list[str] = []
    invalid: list[str] = []

    for name, max_age in DEFAULT_MAX_AGE_HOURS.items():
        item = sources.get(name)
        if not isinstance(item, dict):
            invalid.append(name)
            measurements[name] = {"status": "missing", "current": False}
            continue
        observed = item.get("fetched_at") or item.get("fetched_at_utc")
        try:
            observed_at = parse_time(str(observed))
        except (TypeError, ValueError):
            invalid.append(name)
            measurements[name] = {"status": "invalid_timestamp", "current": False}
            continue
        age_hours = max(0.0, (as_of - observed_at).total_seconds() / 3600)
        current = age_hours <= max_age
        if not current:
            stale.append(name)
        measurements[name] = {
            "status": "current" if current else "stale",
            "current": current,
            "observed_at_utc": observed_at.isoformat().replace("+00:00", "Z"),
            "age_hours": round(age_hours, 3),
            "max_age_hours": max_age,
        }

    trustworthy = not stale and not invalid
    return {
        "schema_version": "1.0",
        "checked_at_utc": as_of.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
        "trustworthy_for_current_decisions": trustworthy,
        "policy": "stale values remain last-observed evidence and must not be called current",
        "stale_sources": stale,
        "invalid_sources": invalid,
        "measurements": measurements,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path, help="JSON object keyed by measurement source")
    parser.add_argument("--as-of", help="ISO-8601 audit time; defaults to now")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    as_of = parse_time(args.as_of) if args.as_of else datetime.now(timezone.utc)
    result = audit_measurements(
        json.loads(args.input.read_text(encoding="utf-8")), as_of
    )
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["trustworthy_for_current_decisions"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
