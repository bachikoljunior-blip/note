#!/usr/bin/env python3
"""check_failure_classes.py が、落とすと言っている失敗を実際に落とすか試す。

**通ることの確認だけでは、検査が何もしていない場合と区別がつかない。**
2026-08-08 の教訓そのもので、この検査自身にも同じ基準を当てる。

    python scripts/test_failure_classes.py
"""
from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "state" / "failure_classes.json"
CHECKER = ROOT / "scripts" / "check_failure_classes.py"


def run(data: dict) -> tuple[int, dict]:
    original = DATA.read_text(encoding="utf-8")
    try:
        DATA.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        proc = subprocess.run([sys.executable, str(CHECKER)], capture_output=True, text=True)
        return proc.returncode, json.loads(proc.stdout)
    finally:
        DATA.write_text(original, encoding="utf-8")


def main() -> int:
    base = json.loads(DATA.read_text(encoding="utf-8"))
    failures: list[str] = []

    def expect_fail(label: str, mutate, needle: str) -> None:
        data = copy.deepcopy(base)
        mutate(data)
        code, out = run(data)
        if code == 0 or out.get("ok"):
            failures.append(f"{label}: 落ちるべきなのに通った")
        elif not any(needle in e for e in out.get("errors", [])):
            failures.append(f"{label}: 落ちたが理由が違う: {out.get('errors')}")
        else:
            print(f"  ok  {label}")

    print("壊したときに落ちるか:")

    # これがこの検査の存在理由。再発したのに質問を足しただけ、を許さない。
    expect_fail(
        "再発しているのに段を上げていないと落ちる",
        lambda d: d["improvable"][0].pop("escalated_at"),
        "段を上げた記録")

    expect_fail(
        "段を上げたと書いて段2のままだと落ちる",
        lambda d: d["improvable"][0].__setitem__("mechanism_level", 2),
        "mechanism_level が 2 のまま")

    expect_fail(
        "改善可能なのに機構が空だと落ちる",
        lambda d: d["improvable"][3].__setitem__("mechanism", ""),
        "mechanism が空")

    # 「不可能」を言い訳の置き場にしないための2件。
    expect_fail(
        "不可能の再検査期限が過ぎていると落ちる",
        lambda d: d["physically_fixed"][0].__setitem__("recheck_after", "2020-01-01"),
        "再検査期限")

    expect_fail(
        "不可能に証拠が無いと落ちる",
        lambda d: d["physically_fixed"][0].__setitem__("evidence", ""),
        "必須の項目がない")

    expect_fail(
        "必須項目が欠けると落ちる",
        lambda d: d["improvable"][0].pop("mechanism_level"),
        "必須項目がない")

    expect_fail(
        "メタが消えると落ちる",
        lambda d: d.pop("meta"),
        "meta がない")

    print("\n壊していないときは通るか:")
    code, out = run(base)
    if code != 0 or not out.get("ok"):
        failures.append(f"無傷の正本が通らない: {out.get('errors')}")
    else:
        print("  ok  正本はそのまま通る")
        print(f"      改善可能 {out['improvable_count']}件 / "
              f"物理的に不可 {out['physically_fixed_count']}件 / "
              f"不可と言ったが解けた {out['solved_after_being_called_impossible']}件")

    print()
    if failures:
        for f in failures:
            print("NG  " + f)
        return 1
    print("すべて通過（8件）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
