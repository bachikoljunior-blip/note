#!/usr/bin/env python3
"""改善ループが実際に回っているかを検査する。

定義は `OPERATIONS/IMPROVEMENT_LOOP.md`、正本は `state/loops.json`。

落とすのは4つ。どれも 2026-08-08 に実際に起きた失敗から来ている。

  1. 測定が古い（121分前の残量を「実測」と報告した）
  2. 3回続けて指標が動かないのに、同じ層の手を続けている
  3. 本人操作が要るループが、0件の代替を検討した記録を持たない
  4. メタループ自身が測られていない（仕組みを作って放置する）

    python scripts/check_loops.py
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOOPS = ROOT / "state" / "loops.json"
REQUIRED = ("id", "metric", "how_to_measure", "measured_at",
            "max_age_hours", "target", "consecutive_no_move")


def parse_time(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def age_hours(stamp: str, now: datetime) -> float | None:
    when = parse_time(stamp)
    if when is None:
        return None
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    return (now - when).total_seconds() / 3600.0


def check_loop(loop: dict, now: datetime, *, is_meta: bool = False) -> list[str]:
    name = loop.get("id", "(id なし)")
    problems: list[str] = []

    for field in REQUIRED:
        if field not in loop:
            problems.append(f"{name}: 必須項目がない: {field}")
    if problems:
        return problems

    aged = age_hours(loop["measured_at"], now)
    if aged is None:
        problems.append(f"{name}: measured_at を時刻として読めない: {loop['measured_at']!r}")
    elif aged > float(loop["max_age_hours"]):
        problems.append(
            f"{name}: 測定が古い（{aged:.1f}時間前 / 上限 {loop['max_age_hours']}時間）。"
            "古い測定は測定ではない。測り直してから判断すること"
        )

    threshold = 3
    if int(loop.get("consecutive_no_move", 0)) >= threshold:
        if not loop.get("approach_changed_at"):
            problems.append(
                f"{name}: {loop['consecutive_no_move']}回続けて指標が動いていないのに、"
                "手法を変えた記録（approach_changed_at）がない。"
                "パラメータではなく層を変えること。動かないなら閉じてよい"
            )

    if int(loop.get("owner_actions_required", 0)) > 0:
        if not loop.get("zero_owner_alternative_considered"):
            problems.append(
                f"{name}: 本人操作が {loop['owner_actions_required']} 件あるのに、"
                "0件の代替を検討した記録（zero_owner_alternative_considered）がない。"
                "オーナーは指示を読むとは限らない"
            )

    if is_meta and not loop.get("revisions"):
        problems.append(f"{name}: メタループに revisions がない。変えた理由が残らない")

    return problems


def main() -> int:
    if not LOOPS.is_file():
        print(json.dumps({"ok": False, "errors": [f"{LOOPS} がない"]}, ensure_ascii=False, indent=2))
        return 1

    data = json.loads(LOOPS.read_text(encoding="utf-8"))
    now = datetime.now(timezone.utc)
    errors: list[str] = []

    loops = data.get("loops", [])
    if not loops:
        errors.append("ループが1つも登録されていない")

    seen: set[str] = set()
    for loop in loops:
        if loop.get("id") in seen:
            errors.append(f"id が重複している: {loop.get('id')}")
        seen.add(loop.get("id"))
        errors.extend(check_loop(loop, now))

    meta = data.get("meta")
    if not meta:
        errors.append("meta（ループ自身のループ）がない。仕組みを作って放置しないため必須")
    else:
        errors.extend(check_loop(meta, now, is_meta=True))

    payload = {
        "ok": not errors,
        "checked_at_utc": now.isoformat(),
        "loop_count": len(loops),
        "loops": [
            {
                "id": l.get("id"),
                "current": l.get("current"),
                "target": l.get("target"),
                "age_hours": round(age_hours(l.get("measured_at", ""), now) or -1, 1),
                "no_move_streak": l.get("consecutive_no_move"),
                "owner_actions": l.get("owner_actions_required"),
            }
            for l in loops
        ],
        "errors": errors,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
