#!/usr/bin/env python3
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from audit_external_measurements import audit_measurements  # noqa: E402


def main() -> int:
    now = datetime(2026, 8, 12, 6, 24, tzinfo=timezone.utc)
    fresh = {
        "usage": {"fetched_at": "2026-08-12T06:00:00Z"},
        "claude_usage": {"fetched_at": "2026-08-12T05:00:00Z"},
        "gumroad_sales": {"fetched_at": "2026-08-12T04:00:00Z"},
        "itch_stats": {"fetched_at": "2026-08-12T04:00:00Z"},
    }
    assert audit_measurements(fresh, now)["trustworthy_for_current_decisions"]

    stale = {key: dict(value) for key, value in fresh.items()}
    stale["usage"] = {"fetched_at": "2026-08-11T19:10:09.544Z"}
    result = audit_measurements(stale, now)
    assert not result["trustworthy_for_current_decisions"]
    assert result["stale_sources"] == ["usage"]
    assert result["measurements"]["usage"]["age_hours"] > 11

    missing = {key: value for key, value in fresh.items() if key != "gumroad_sales"}
    result = audit_measurements(missing, now)
    assert result["invalid_sources"] == ["gumroad_sales"]
    assert not result["trustworthy_for_current_decisions"]

    print("external measurement freshness audit: all tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
