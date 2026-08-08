#!/usr/bin/env python3
"""失敗のクラスごとに、直し方が実際に効いているかを検査する。

正本は `state/failure_classes.json`、定義は `OPERATIONS/FAILURE_CLASSES.md`。

## なぜ要るか

2026-08-08、**失敗するたびに終了前フックへ質問を足していた。**
Q5・Q6 を `bc168df`（09:27Z）で足し、その後に同じ種類の失敗が **3回** 起きた。

つまり「直した」と言っていたものが、実測で直っていなかった。
**足したこと自体が、直した証拠として通用してしまっていた。**

だからこの検査は、直し方そのものに段位を付ける。

  1. 文書に書く       —— 恒久指示は文脈に在り続けたまま3回破られた
  2. 質問を足す       —— 足した後に3回破られた
  3. 機械が落とす     —— 人が答えを書く余地が無い
  4. 道具を変える     —— 間違った値が手に入らないようにする

**再発したら段を上げる。質問を足すのは段を上げたことにならない。**

## もう一つ ——「不可能」を言い訳の置き場にしない

オーナーの提案は「実行したものを、改善できるものと物理的に不可能なものへ振り分け、
改善できるものにループを設計する」。採用したうえで、不可の側に期限を足した。

理由は実測。**2026-08-08 に「不可能」と判定したもののうち2つが、同じ日に解けた。**
環境変数はセッションを新しくすれば入り、到達できないサイトは手元にミラーすれば見られた。
期限が無ければ、この2つは今も「できないこと」の欄に残っていた。

落とすのは6つ。

  1. 必須項目がない
  2. 再発しているのに段を上げた記録がない
  3. 改善可能なのに機構がない
  4. 不可能と判定したのに証拠がない、または再検査期限がない
  5. **再検査期限が過ぎている**（不可の欄を放置させない）
  6. メタが測られていない

    python scripts/check_failure_classes.py
"""
from __future__ import annotations

import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "state" / "failure_classes.json"

REQUIRED = ("id", "what", "instances", "mechanism", "mechanism_level",
            "mechanism_added_at", "recurred_after_fix")
REQUIRED_FIXED = ("id", "what", "evidence", "recheck_after")


def parse_day(value: str) -> date | None:
    try:
        return date.fromisoformat(str(value)[:10])
    except (ValueError, TypeError):
        return None


def check_improvable(item: dict) -> list[str]:
    name = item.get("id", "(id なし)")
    problems: list[str] = []

    for field in REQUIRED:
        if field not in item:
            problems.append(f"{name}: 必須項目がない: {field}")
    if problems:
        return problems

    try:
        level = int(item["mechanism_level"])
    except (TypeError, ValueError):
        return [f"{name}: mechanism_level を数として読めない: {item['mechanism_level']!r}"]

    if not 1 <= level <= 4:
        problems.append(f"{name}: mechanism_level は 1〜4: {level}")

    if not str(item.get("mechanism") or "").strip():
        problems.append(f"{name}: 改善可能なのに mechanism が空。何で防ぐのかを書くこと")

    # ここが本体。再発したのに段を上げていないなら落とす。
    try:
        recurred = int(item.get("recurred_after_fix", 0))
    except (TypeError, ValueError):
        recurred = 0

    if recurred > 0 and not item.get("escalated_at"):
        problems.append(
            f"{name}: 機構を入れた後に {recurred} 回再発しているのに、"
            "段を上げた記録（escalated_at）がない。"
            "**質問を足すのは段を上げたことにならない。** 機械が落とすか、道具を変えること"
        )

    if recurred > 0 and item.get("escalated_at") and level <= 2:
        problems.append(
            f"{name}: 再発して段を上げたと書いてあるのに mechanism_level が {level} のまま。"
            "段3（機械が落とす）以上にすること"
        )

    return problems


def check_fixed(item: dict, today: date) -> list[str]:
    name = item.get("id", "(id なし)")
    problems: list[str] = []

    for field in REQUIRED_FIXED:
        if field not in item or not str(item.get(field) or "").strip():
            problems.append(f"{name}: 不可能と判定するのに必須の項目がない、または空: {field}")
    if problems:
        return problems

    when = parse_day(item["recheck_after"])
    if when is None:
        problems.append(f"{name}: recheck_after を日付として読めない: {item['recheck_after']!r}")
    elif when < today:
        problems.append(
            f"{name}: 再検査期限（{item['recheck_after']}）を過ぎている。"
            "測り直して、まだ不可能なら期限を延ばすこと。"
            "**2026-08-08 に『不可能』としたもののうち2つが同じ日に解けている。**"
            "期限のない不可は、ただの言い訳になる"
        )

    return problems


def main() -> int:
    if not DATA.is_file():
        print(json.dumps({"ok": False, "errors": [f"{DATA} がない"]},
                         ensure_ascii=False, indent=2))
        return 1

    data = json.loads(DATA.read_text(encoding="utf-8"))
    today = datetime.now(timezone.utc).date()
    errors: list[str] = []

    improvable = data.get("improvable", [])
    if not improvable:
        errors.append("improvable が空。失敗が1件も分類されていない")

    seen: set[str] = set()
    for item in improvable:
        if item.get("id") in seen:
            errors.append(f"id が重複している: {item.get('id')}")
        seen.add(item.get("id"))
        errors.extend(check_improvable(item))

    for item in data.get("physically_fixed", []):
        if item.get("id") in seen:
            errors.append(f"id が重複している: {item.get('id')}")
        seen.add(item.get("id"))
        errors.extend(check_fixed(item, today))

    meta = data.get("meta")
    if not meta:
        errors.append("meta がない。この仕組み自身が測られない")
    else:
        if not meta.get("revisions"):
            errors.append("meta に revisions がない。変えた理由が残らない")
        if not str(meta.get("consumer") or "").strip():
            errors.append("meta に consumer がない。誰が読んで動くのかを書くこと")

    unescalated = [i.get("id") for i in improvable
                   if int(i.get("recurred_after_fix", 0) or 0) > 0 and not i.get("escalated_at")]

    payload = {
        "ok": not errors,
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "improvable_count": len(improvable),
        "physically_fixed_count": len(data.get("physically_fixed", [])),
        "solved_after_being_called_impossible":
            len(data.get("was_called_impossible_but_was_not", [])),
        "recurred_without_escalation": unescalated,
        "mechanism_levels": {
            i.get("id"): i.get("mechanism_level") for i in improvable
        },
        "errors": errors,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
