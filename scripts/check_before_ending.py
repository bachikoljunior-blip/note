#!/usr/bin/env python3
"""終わってよいかを、機械が計算する。

## なぜ質問ではだめだったか

2026-08-08、終了前フックに「まだ高価値作業はないか」「あとで自動実行が拾うから、
で終えていないか」という質問を足した（`bc168df` 09:27Z）。
**その後、同じ種類の失敗が3回起きた。**

質問の弱点は、**答えを自分で書けること**。「無い」と書けば通る。
だからこの検査は、質問をやめて **残っているものを数える**。

出すのは4つ。どれも実測で、記憶ではない。

  1. 使ってよい資源の残量（Claude / Codex / Spark）
  2. 測定が古くなったループ
  3. 未確認のまま置かれている検証（watchdogs の pending_verification）
  4. 再発したのに段を上げていない失敗クラス

**1つでも残っていれば exit 1。**「やることが無い」と言うには、
まずこの検査を黙らせる必要がある —— 資源を使うか、測り直すか、確かめるか、段を上げるか。

黙らせずに終えてよい場合はある。ただし **その理由を自分の言葉で述べること**が要る。
検査は終了を禁止しない。**「何も残っていない」と言えなくするだけ。**

    python scripts/check_before_ending.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
USAGE_REPOS = (
    Path("/home/user/-chatgpt-usage-monitorPrivate"),
    ROOT.parent / "-chatgpt-usage-monitorPrivate",
)


def read_usage() -> list[str]:
    """使える資源が残っているかを、実測で言う。読めなければ、読めないと言う。"""
    out: list[str] = []
    for repo in USAGE_REPOS:
        script = repo / "scripts" / "show-usage.mjs"
        if not script.is_file():
            continue
        try:
            proc = subprocess.run(["node", str(script)], cwd=str(repo),
                                  capture_output=True, text=True, timeout=60)
        except (OSError, subprocess.SubprocessError) as exc:
            return [f"使用量を読めなかった: {exc}"]
        for line in proc.stdout.splitlines():
            line = line.strip()
            if not line or line.startswith("Stale or missing"):
                continue
            out.append(line)
        return out
    return ["使用量の測定器が見つからない（-chatgpt-usage-monitorPrivate が無い）"]


def age_hours(stamp: str, now: datetime) -> float | None:
    try:
        when = datetime.fromisoformat(str(stamp).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    return (now - when).total_seconds() / 3600.0


def load(name: str) -> dict:
    path = ROOT / "state" / name
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def goal_report(now: datetime) -> tuple[list[str], list[str]]:
    """A1 に対していまいくらか。**最初に見る。**

    オーナーの提案（2026-08-08）: 毎回、最後に目標が達成できているかと
    最新の使用量を確認してから、終わるのが最善かを考える。

    それまでこの検査は使用量と残作業しか見ておらず、
    **目標への距離を一度も見ずに「終わってよいか」を判断していた。** 順番が逆だった。
    """
    goal = load("goal.json")
    if not goal:
        return (["state/goal.json が無い。目標への距離を測れない"],
                ["目標の登録簿が無い。A1 に対する現在地が誰にも分からない状態"])

    target = float(goal.get("target_jpy_per_month") or 0)
    lines: list[str] = []
    problems: list[str] = []
    total = 0.0

    for src in goal.get("sources", []):
        value = float(src.get("current_jpy_per_month") or 0)
        total += value
        aged = age_hours(src.get("measured_at", ""), now)
        try:
            limit = float(src.get("max_age_hours") or 0)
        except (TypeError, ValueError):
            limit = 0.0
        stale = aged is not None and limit and aged > limit
        mark = "  ← 測定が古い" if stale else ""
        lines.append(f"  {src.get('id'):<20} ¥{value:>10,.0f}/月"
                     f"  ({aged:.1f}時間前){mark}" if aged is not None
                     else f"  {src.get('id'):<20} ¥{value:>10,.0f}/月  (測定時刻不明)")
        if aged is not None and aged < -0.05:
            problems.append(
                f"目標の内訳 {src.get('id')} の measured_at が未来（{-aged:.1f}時間先）。"
                "測っていない時刻を書いている")
        if stale:
            problems.append(f"目標の内訳 {src.get('id')} の測定が古い（{aged:.1f}時間前）")
        if src.get("blocker"):
            lines.append(f"  {'':<20}   律速: {src['blocker']}")

    pct = (total / target * 100.0) if target else 0.0
    header = [f"目標（A1）: 月 ¥{target:,.0f}",
              f"現在      : ¥{total:,.0f}  = {pct:.1f}%",
              f"残り      : ¥{target - total:,.0f}", ""]

    for gate in goal.get("gates", []):
        aged = age_hours(gate.get("measured_at", ""), now)
        cur = gate.get("current", {})
        lines.append(f"  門 {gate.get('id')}: {json.dumps(cur, ensure_ascii=False)}"
                     + (f"  ({aged:.1f}時間前)" if aged is not None else ""))

    if total < target:
        lines.append("")
        lines.append("  **未達です。終わる理由を目標側から持ってくることはできません。**")
        if goal.get("honest_note"):
            lines.append("  " + str(goal["honest_note"]))

    return header + lines, problems


def main() -> int:
    now = datetime.now(timezone.utc)
    remaining: list[str] = []

    goal_lines, goal_problems = goal_report(now)
    remaining.extend(goal_problems)

    usage_lines = read_usage()
    stale_usage = any("STALE" in l for l in usage_lines)
    if stale_usage:
        remaining.append("使用量が STALE。残量を理由にするなら、まず測り直すこと")

    loops = load("loops.json")
    for loop in loops.get("loops", []):
        aged = age_hours(loop.get("measured_at", ""), now)
        try:
            limit = float(loop.get("max_age_hours", 0))
        except (TypeError, ValueError):
            limit = 0.0
        if aged is not None and limit and aged > limit:
            remaining.append(
                f"ループ {loop.get('id')} の測定が古い（{aged:.1f}時間前 / 上限 {limit}）")

    watchdogs = load("watchdogs.json")
    for w in watchdogs.get("watchdogs", []):
        pv = w.get("pending_verification")
        if not pv or pv.get("resolved_at"):
            continue
        wid = w.get("id")
        deadline = pv.get("deadline_utc")
        past = age_hours(deadline, now) if deadline else None
        if past is not None and past > 0:
            # 期限を過ぎても期待した信号が来ていない。ここを「未確認」で流さない。
            remaining.append(
                f"**{wid}: 期限（{deadline}）を {past:.1f}時間 過ぎても信号が来ていない。"
                f"期待した信号は「{pv.get('expected_signal')}」。"
                "『まだ確認できていない』ではなく**不作動を疑うこと。** "
                "作った仕組みが動いていない可能性を先に潰す**")
        elif "未確認" in str(pv.get("status", "")):
            remaining.append(
                f"ウォッチドッグ {wid} に未確認の検証がある: {pv.get('what')}"
                + (f"（期限 {deadline}）" if deadline else ""))

    classes = load("failure_classes.json")
    for item in classes.get("improvable", []):
        try:
            recurred = int(item.get("recurred_after_fix", 0) or 0)
        except (TypeError, ValueError):
            recurred = 0
        if recurred > 0 and not item.get("escalated_at"):
            remaining.append(
                f"失敗クラス {item.get('id')} が再発しているのに段を上げていない")
    today = now.date()
    for item in classes.get("physically_fixed", []):
        try:
            when = datetime.fromisoformat(str(item.get("recheck_after"))[:10]).date()
        except (ValueError, TypeError):
            continue
        if when < today:
            remaining.append(
                f"「不可能」と判定した {item.get('id')} の再検査期限が過ぎている。測り直すこと")

    print("── 1. 目標は達成できているか（A1・実測） ──")
    for line in goal_lines:
        print(line if line.startswith("  ") or not line else "  " + line)
    print()
    print("── 2. 使ってよい資源（実測・最新か） ──")
    for line in usage_lines:
        print("  " + line)
    print()
    if remaining:
        print("── 3. まだ残っているもの ──")
        for r in remaining:
            print("  ・" + r)
        print()
        print("── 4. 判定 ──")
        print("「やることが無い」とは言えません。使うか、測り直すか、確かめるか、段を上げること。")
        print("それでも終えるなら、**残っているものを名指しして、なぜ今やらないかを述べること。**")
    else:
        print("── 3. まだ残っているもの ──")
        print("  （検査が見つけた範囲では無し）")
        print()
        print("この検査が見ているのは4つだけです。**見ていないものが無いことの証明にはなりません。**")

    return 1 if remaining else 0


if __name__ == "__main__":
    sys.exit(main())
