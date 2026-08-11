#!/usr/bin/env python3
"""改善ループが実際に回っているかを検査する。

定義は `OPERATIONS/IMPROVEMENT_LOOP.md`、正本は `state/loops.json`。

落とすのは5つ。どれも 2026-08-08 に実際に起きた失敗から来ている。

  1. 測定が古い（121分前の残量を「実測」と報告した）
  2. 3回続けて指標が動かないのに、同じ層の手を続けている
  3. 本人操作が要るループが、0件の代替を検討した記録を持たない
  4. メタループ自身が測られていない（仕組みを作って放置する）
  5. 測定を、それで動く相手が読まない場所に書いている（consumer 未記入）

5番目の来歴。尺と再生の関係を測って state/loops.json に書いたが、
実際に投稿を決めるのはクッキー日次実行で、それが読むのは
promo/youtube/JOURNAL.md だった。**測定は正しく、置き場所だけが間違っていた。**
測っただけで届いていないのは、測っていないのとほぼ同じ結果になる。
だから各ループに「誰が読んで動くか」を必ず書かせる。

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
            "max_age_hours", "target", "consecutive_no_move", "consumer")


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


def check_effect_window(loop: dict, now: datetime) -> list[str]:
    """判断時刻を過ぎた観測が窓前のまま残らないことを検査する。"""
    name = loop.get("id", "(id なし)")
    observation = loop.get("latest_observation")
    if not isinstance(observation, dict):
        return []
    if "decision_not_before_utc" not in observation:
        return []

    problems: list[str] = []
    raw_decision = observation.get("decision_not_before_utc")
    decision = parse_time(raw_decision)
    if decision is None or decision.tzinfo is None or decision.utcoffset() is None:
        return [
            f"{name}: decision_not_before_utc はタイムゾーン付き日時であること"
        ]

    elapsed = observation.get("effect_window_elapsed")
    if not isinstance(elapsed, bool):
        problems.append(f"{name}: effect_window_elapsed は真偽値であること")
    elif now >= decision and elapsed is not True:
        problems.append(
            f"{name}: decision_not_before_utc を過ぎたのに "
            "effect_window_elapsed=false のまま。期限後の実測へ更新すること"
        )
    elif now < decision and elapsed is True:
        problems.append(
            f"{name}: decision_not_before_utc より前なのに "
            "effect_window_elapsed=true。効果窓を先取りしないこと"
        )

    conclusion_allowed = observation.get("performance_conclusion_allowed")
    if not isinstance(conclusion_allowed, bool):
        problems.append(
            f"{name}: performance_conclusion_allowed は真偽値であること"
        )
    return problems


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
    elif aged < -0.05:
        problems.append(
            f"{name}: measured_at が未来（{-aged:.1f}時間先）。"
            "測っていない時刻を書いている。2026-08-08 に2回やった（loops.json と goal.json）。"
            "datetime.now(timezone.utc) の戻り値を使うこと"
        )
    elif aged > float(loop["max_age_hours"]):
        problems.append(
            f"{name}: 測定が古い（{aged:.1f}時間前 / 上限 {loop['max_age_hours']}時間）。"
            "古い測定は測定ではない。測り直してから判断すること"
        )

    problems.extend(check_effect_window(loop, now))

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
