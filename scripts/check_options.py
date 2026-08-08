#!/usr/bin/env python3
"""既存のものにとらわれていないかを検査する。

正本は `state/options.json`。

## なぜ要るか

2026-08-08 のオーナーの指摘。

> 既存のものにとらわれてない？既存のものにとらわれない設計にして。

そのとおりだった。**その日に作った仕組みは全部、すでに在るものを守る機械だった。**

  `loops.json`          —— いま回している workstream を列挙する
  `watchdogs.json`      —— いま在る監視対象を列挙する
  `failure_classes.json`—— すでに起きた失敗を列挙する
  `goal.json`           —— **いま持っている収入源だけ**を足し上げる

どれも「在るもの」しか入らない。**私が入れたものしか入らず、私が入れたのは
既存のものだけだった。** だから、この一式をどれだけ丁寧に回しても、
**「この資産の組み合わせが間違っている」には永久に到達できない。**

8か月ぶん作業があって0円、という事実に対して、
仕組みの側が「今の路線を続ける」以外の答えを出せない形になっていた。

## だからこの登録簿は、既存で埋まらないようにする

落とすのは5つ。

  1. 未検証かつ非既存の選択肢が `min_untested_non_incumbent` 件に満たない
     —— **登録簿が「いまやっていることの一覧」に退化するのを防ぐ**
  2. 既存（incumbent）の選択肢に kill_date が無い
     —— 撤退の期限が無いものは、永久に続けられる
  3. kill_date を過ぎているのに判断の記録が無い
  4. 最初の1円までの見込み日数が無い
     —— 比較できない案は、比較されずに温存される
  5. メタが測られていない

## 撤退規則

**既存が続いてよいのは、未検証の最良案より「最初の1円までが速い」と
言えるときだけ。** 言えないなら、既存を閉じるか、資源を移すこと。
「もう作ってあるから」は理由にならない（A14: 昔そう言ったから、は理由にならない）。

    python scripts/check_options.py
"""
from __future__ import annotations

import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "state" / "options.json"

REQUIRED = ("id", "what", "incumbent", "days_to_first_yen",
            "owner_actions_required", "tested")


def parse_day(value: str) -> date | None:
    try:
        return date.fromisoformat(str(value)[:10])
    except (ValueError, TypeError):
        return None


def check_one(o: dict, today: date) -> list[str]:
    name = o.get("id", "(id なし)")
    problems: list[str] = []

    for field in REQUIRED:
        if field not in o:
            problems.append(f"{name}: 必須項目がない: {field}")
    if problems:
        return problems

    # 「到達不能」は空欄ではなく、立派な測定結果。区別する。
    # 空欄のまま置くと比較されずに温存されるが、unreachable と書けば
    # 順位の最後に落ちて、収入源として数えられなくなる。
    dtfy = o.get("days_to_first_yen")
    if dtfy in (None, ""):
        problems.append(
            f"{name}: days_to_first_yen が空。**比較できない案は温存される。**"
            "到達不能なら 'unreachable' と書くこと。分からないなら根拠つきの範囲を書くこと")
    elif dtfy == "unreachable" and not str(o.get("days_to_first_yen_note") or "").strip():
        problems.append(
            f"{name}: 到達不能と書くなら、なぜ到達しないのかを "
            "days_to_first_yen_note に書くこと")

    if o.get("incumbent"):
        if not o.get("kill_date"):
            problems.append(
                f"{name}: 既存なのに kill_date が無い。"
                "**撤退期限の無いものは永久に続けられる。** "
                "いつまでに1円入らなければ閉じるのかを書くこと")
        else:
            when = parse_day(o["kill_date"])
            if when is None:
                problems.append(f"{name}: kill_date を日付として読めない: {o['kill_date']!r}")
            elif when < today and not o.get("kill_decision"):
                problems.append(
                    f"{name}: kill_date（{o['kill_date']}）を過ぎているのに判断の記録"
                    "（kill_decision）が無い。閉じるか、未検証の最良案より速い理由を書くこと")

    return problems


def main() -> int:
    if not DATA.is_file():
        print(json.dumps({"ok": False, "errors": [f"{DATA} がない"]},
                         ensure_ascii=False, indent=2))
        return 1

    data = json.loads(DATA.read_text(encoding="utf-8"))
    today = datetime.now(timezone.utc).date()
    errors: list[str] = []

    options = data.get("options", [])
    if not options:
        errors.append("選択肢が1つも登録されていない")

    seen: set[str] = set()
    for o in options:
        if o.get("id") in seen:
            errors.append(f"id が重複している: {o.get('id')}")
        seen.add(o.get("id"))
        errors.extend(check_one(o, today))

    # ここがこの検査の存在理由。
    # 未検証かつ非既存の案が一定数ないと、登録簿は「いまやっていること」に退化する。
    quota = int(data.get("min_untested_non_incumbent", 3) or 3)
    fresh = [o for o in options if not o.get("incumbent") and not o.get("tested")]
    if len(fresh) < quota:
        errors.append(
            f"未検証かつ非既存の選択肢が {len(fresh)} 件しかない（下限 {quota}）。"
            "**登録簿が『いまやっていることの一覧』に退化している。** "
            "既存の外側を先に増やすこと"
        )

    meta = data.get("meta")
    if not meta:
        errors.append("meta がない。この登録簿自身が測られない")
    elif not meta.get("revisions"):
        errors.append("meta に revisions がない。増やした理由と、捨てた案が残らない")

    def sort_key(o: dict) -> float:
        v = o.get("days_to_first_yen")
        if isinstance(v, (int, float)):
            return float(v)
        if isinstance(v, dict) and isinstance(v.get("low"), (int, float)):
            return float(v["low"])
        return 1e9

    ranked = sorted(options, key=sort_key)
    best_fresh = next((o for o in ranked if not o.get("incumbent")), None)

    payload = {
        "ok": not errors,
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "option_count": len(options),
        "incumbents": sum(1 for o in options if o.get("incumbent")),
        "untested_non_incumbent": len(fresh),
        "fastest_overall": ranked[0].get("id") if ranked else None,
        "fastest_non_incumbent": best_fresh.get("id") if best_fresh else None,
        "errors": errors,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
