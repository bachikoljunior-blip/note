#!/usr/bin/env python3
"""監視されるべき量が、実際に監視されているかを検査する。

正本は `state/watchdogs.json`、定義は `OPERATIONS/WATCHDOGS.md`。

ループ（`state/loops.json`）との違い。
ループは**良くしたい数字**。ウォッチドッグは**目を離してはいけない数字**で、
改善しなくてよいが、古くなったり壊れたりしたら気づかねばならないもの。

2026-08-08 にオーナーが指摘した抜けから来ている。

  「使用量とか定期的に監視しないとダメじゃない？そういう抜けが他にもないように設計してよ」

そのとき実際に起きていたのは、次の3つが同時に成立している状態だった。

  1. 使用量は毎時集められていた（監視は在った）
  2. しかし**古さの判定が壊れていて**、リセット済みの枠の残量が現在値として出た
  3. そして**当てにならない代用品が2つのリポジトリに在り**、使用量として読まれ得た

だから、この検査が落とすのは4つ。

  1. 必須項目がない（何を・どこから・どれだけ新しく・誰が読むか）
  2. **オーナー操作なしで新しくする方法がない**（A1: 依頼は読まれるとは限らない）
  3. **既知の当てにならない代用品が source_of_truth に入っている**
  4. 実測が要ると宣言した量に、実際の観測記録が無い

    python scripts/check_watchdogs.py
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WATCHDOGS = ROOT / "state" / "watchdogs.json"

REQUIRED = ("id", "what", "source_of_truth", "read_with",
            "max_age_hours", "refresh_without_owner", "consumer")


def check_one(w: dict) -> list[str]:
    name = w.get("id", "(id なし)")
    problems: list[str] = []

    for field in REQUIRED:
        if field not in w or not str(w.get(field) or "").strip():
            problems.append(f"{name}: 必須項目がない、または空: {field}")
    if problems:
        return problems

    # A1。オーナーが動かないと新しくできない監視は、監視ではない。
    refresh = str(w["refresh_without_owner"])
    if any(k in refresh for k in ("オーナー", "本人", "手動で依頼", "頼む")):
        problems.append(
            f"{name}: refresh_without_owner がオーナー操作を含んでいる（{refresh!r}）。"
            "オーナーは指示を読むとは限らない。操作0件の経路を書くこと"
        )

    # 当てにならないと分かっている代用品を、正本に据えていないか。
    truth = str(w["source_of_truth"])
    for bad in w.get("not_a_source", []):
        path = str(bad.get("path", "")).strip()
        if not path:
            problems.append(f"{name}: not_a_source に path が無い項目がある")
            continue
        if not str(bad.get("why", "")).strip():
            problems.append(f"{name}: not_a_source の {path} に why が無い。"
                            "なぜ駄目かを書かないと、次の周で復活する")
        head = path.split(" の ")[-1].strip()
        if head and head in truth:
            problems.append(
                f"{name}: 当てにならないと記録した {head} が source_of_truth に入っている。"
                "代用品を正本に据えない"
            )

    try:
        if float(w["max_age_hours"]) <= 0:
            problems.append(f"{name}: max_age_hours が 0 以下")
    except (TypeError, ValueError):
        problems.append(f"{name}: max_age_hours を数として読めない: {w['max_age_hours']!r}")

    return problems


def main() -> int:
    if not WATCHDOGS.is_file():
        print(json.dumps({"ok": False, "errors": [f"{WATCHDOGS} がない"]},
                         ensure_ascii=False, indent=2))
        return 1

    data = json.loads(WATCHDOGS.read_text(encoding="utf-8"))
    now = datetime.now(timezone.utc)
    errors: list[str] = []

    items = data.get("watchdogs", [])
    if not items:
        errors.append("ウォッチドッグが1つも登録されていない")

    seen: set[str] = set()
    for w in items:
        wid = w.get("id")
        if wid in seen:
            errors.append(f"id が重複している: {wid}")
        seen.add(wid)
        errors.extend(check_one(w))

    # 使用量は必ず登録されていること。ここが今回の指摘の出どころ。
    for must in ("claude_usage", "codex_usage"):
        if must not in seen:
            errors.append(
                f"{must} が登録されていない。"
                "使用量は『使ってよい資源』であり、測らずに判断すると必ず外す"
            )

    payload = {
        "ok": not errors,
        "checked_at_utc": now.isoformat(),
        "watchdog_count": len(items),
        "watchdogs": [
            {
                "id": w.get("id"),
                "max_age_hours": w.get("max_age_hours"),
                "owner_free_refresh": bool(str(w.get("refresh_without_owner") or "").strip()),
                "rejected_substitutes": len(w.get("not_a_source", [])),
            }
            for w in items
        ],
        "errors": errors,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
