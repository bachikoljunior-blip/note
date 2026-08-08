#!/usr/bin/env python3
"""tools/verified.py の契約を検査する。

守りたいのは2つ。どちらも 2026-08-08 に実際に破って、実害が出た。

  1. 書いた結果を読み直し、食い違ったら **止まる**（黙って進まない）
  2. 「無い」を1つの観測で言おうとしたら **止まる**
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.verified import (  # noqa: E402
    InsufficientObservations,
    VerificationError,
    absent,
    write_and_verify,
)

FAILURES: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"{'PASS' if ok else 'FAIL'}  {label}{('  — ' + detail) if detail else ''}")
    if not ok:
        FAILURES.append(label)


def main() -> int:
    # 1. 素直に通る場合
    store = {}
    write_and_verify(label="ふつうの書き込み",
                     write=lambda: store.update(v="3800"),
                     read=lambda: store["v"], expect="3800", attempts=1)
    check("一致すれば通る", store["v"] == "3800")

    # 2. 反映が遅れる場合（実測: YouTube も Gumroad も初回の読みは古い値を返した）
    lag = {"reads": 0, "v": "old"}

    def slow_read():
        lag["reads"] += 1
        return "new" if lag["reads"] >= 3 else "old"

    write_and_verify(label="反映が遅い書き込み", write=lambda: None,
                     read=slow_read, expect="new", attempts=5, delay_seconds=0)
    check("遅れて反映されても通る", lag["reads"] == 3, f"{lag['reads']}回読んだ")

    # 3. 応答は success でも値が変わらない場合（通貨変更でこれを踏んだ）
    try:
        write_and_verify(label="黙って無視される書き込み",
                         write=lambda: {"success": True},
                         read=lambda: "usd", expect="jpy", attempts=2, delay_seconds=0)
        check("値が変わらなければ止まる", False, "止まらなかった")
    except VerificationError as exc:
        check("値が変わらなければ止まる", "usd" in str(exc))

    # 4. 基準を渡さなければ拒否する（通す意味が無いので）
    try:
        write_and_verify(label="基準なし", write=lambda: None, read=lambda: 1)
        check("読み直しの基準が無ければ拒否する", False, "拒否しなかった")
    except ValueError:
        check("読み直しの基準が無ければ拒否する", True)

    # 5. 不在を1つの観測で言おうとしたら止まる
    try:
        absent("チャンネルのリンク", [("channels.list", lambda: True)])
        check("観測1つでの不在主張は止まる", False, "止まらなかった")
    except InsufficientObservations as exc:
        check("観測1つでの不在主張は止まる", "1 個しかない" in str(exc))

    # 6. 2つ揃えば通る
    check("観測2つで一致すれば不在と言える",
          absent("本当に無いもの",
                 [("api", lambda: True), ("html", lambda: True)]) is True)

    # 7. 片方で見つかったら止まる（今日2回踏んだ形）
    try:
        absent("毎時自動実行",
               [("list_triggers", lambda: True), ("commitの時刻分布", lambda: False)])
        check("片方で見つかれば止まる", False, "止まらなかった")
    except VerificationError as exc:
        check("片方で見つかれば止まる", "commitの時刻分布" in str(exc))

    print()
    if FAILURES:
        print(f"{len(FAILURES)}件が失敗しました: " + ", ".join(FAILURES))
        return 1
    print("すべて通りました。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
