#!/usr/bin/env python3
"""check_watchdogs.py が、落とすと言っている失敗を実際に落とすか試す。

通ることの確認だけでは意味がない。**壊したときに落ちること**を確かめる。
2026-08-08、「直した」と言って読み直さなかった失敗を8回している。

    python scripts/test_watchdogs.py
"""
from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WATCHDOGS = ROOT / "state" / "watchdogs.json"
CHECKER = ROOT / "scripts" / "check_watchdogs.py"


def run(data: dict) -> tuple[int, dict]:
    """壊したデータで検査を走らせ、終了コードと出力を返す。正本は必ず戻す。"""
    original = WATCHDOGS.read_text(encoding="utf-8")
    try:
        WATCHDOGS.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                             encoding="utf-8")
        proc = subprocess.run([sys.executable, str(CHECKER)],
                              capture_output=True, text=True)
        return proc.returncode, json.loads(proc.stdout)
    finally:
        WATCHDOGS.write_text(original, encoding="utf-8")


def main() -> int:
    base = json.loads(WATCHDOGS.read_text(encoding="utf-8"))
    failures: list[str] = []

    def expect_fail(label: str, mutate, needle: str) -> None:
        data = copy.deepcopy(base)
        mutate(data)
        code, out = run(data)
        if code == 0 or out.get("ok"):
            failures.append(f"{label}: 落ちるべきなのに通った")
            return
        if not any(needle in e for e in out.get("errors", [])):
            failures.append(f"{label}: 落ちたが理由が違う: {out.get('errors')}")
            return
        print(f"  ok  {label}")

    print("壊したときに落ちるか:")

    expect_fail(
        "使用量の監視を消すと落ちる",
        lambda d: d["watchdogs"].__setitem__(
            slice(None), [w for w in d["watchdogs"] if w["id"] != "claude_usage"]),
        "claude_usage が登録されていない")

    expect_fail(
        "更新にオーナー操作が要ると落ちる",
        lambda d: d["watchdogs"][0].__setitem__("refresh_requires_owner", True),
        "オーナー操作が要る")

    expect_fail(
        "オーナー操作の要否を書いていないと落ちる",
        lambda d: d["watchdogs"][0].pop("refresh_requires_owner"),
        "refresh_requires_owner")

    # 語を避けただけでは通らないこと。**書き方の調整で抜けられる検査は検査ではない。**
    expect_fail(
        "本文から「オーナー」を消してもフラグが真なら落ちる",
        lambda d: (d["watchdogs"][0].__setitem__("refresh_without_owner", "手で入れ直す"),
                   d["watchdogs"][0].__setitem__("refresh_requires_owner", True)),
        "オーナー操作が要る")

    expect_fail(
        "当てにならない代用品を正本に据えると落ちる",
        lambda d: d["watchdogs"][0].__setitem__(
            "source_of_truth", "promo/youtube/usage.mjs から推定する"),
        "source_of_truth に入っている")

    expect_fail(
        "必須項目が欠けると落ちる",
        lambda d: d["watchdogs"][0].pop("consumer"),
        "必須項目がない")

    expect_fail(
        "代用品に理由が無いと落ちる",
        lambda d: d["watchdogs"][0]["not_a_source"][0].__setitem__("why", ""),
        "why が無い")

    print("\n壊していないときは通るか:")
    code, out = run(base)
    if code != 0 or not out.get("ok"):
        failures.append(f"無傷の正本が通らない: {out.get('errors')}")
    else:
        print("  ok  正本はそのまま通る")

    print()
    if failures:
        for f in failures:
            print("NG  " + f)
        return 1
    print("すべて通過（6件）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
