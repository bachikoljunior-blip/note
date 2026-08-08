#!/usr/bin/env python3
"""directive_guard.py の契約を検査する。

守りたい性質は2つだけで、どちらも壊れると実害が出る。
  1. Stop は1ユーザーターンにつき **ちょうど1回** 止める。
     0回だと A9 が発火しない。毎回だと終われなくなる。
  2. ユーザー発言でリセットされる。されないとセッション中1回しか効かない。
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUARD = ROOT / "tools" / "directive_guard.py"
FAILURES: list[str] = []


def run(mode: str, session: str, home: Path) -> tuple[int, str]:
    env = dict(os.environ, HOME=str(home))
    result = subprocess.run(
        [sys.executable, str(GUARD), mode],
        input=json.dumps({"session_id": session}),
        capture_output=True, text=True, env=env,
    )
    return result.returncode, result.stdout


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"{'PASS' if ok else 'FAIL'}  {label}{('  — ' + detail) if detail else ''}")
    if not ok:
        FAILURES.append(label)


def decision(out: str) -> str | None:
    try:
        return json.loads(out).get("decision")
    except Exception:  # noqa: BLE001
        return None


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        home = Path(tmp)

        code, out = run("session-start", "s1", home)
        payload = json.loads(out)
        context = payload["hookSpecificOutput"]["additionalContext"]
        check("SessionStart が恒久指示を文脈へ入れる", "A13" in context and "A9" in context)
        check("SessionStart は止めない", code == 0 and "decision" not in payload)

        check("Stop 1回目は止める", decision(run("stop", "s1", home)[1]) == "block")
        check("Stop 2回目は通す（デッドロックしない）", decision(run("stop", "s1", home)[1]) is None)
        check("Stop 3回目も通す", decision(run("stop", "s1", home)[1]) is None)

        run("prompt-submit", "s1", home)
        check("ユーザー発言でリセットされ、また止める",
              decision(run("stop", "s1", home)[1]) == "block")

        check("別セッションは独立している", decision(run("stop", "s2", home)[1]) == "block")

        # HOME が書けなくてもセッションを壊さない
        unwritable = Path(tmp) / "nope"
        code, out = run("stop", "s3", unwritable / "deeper" / "deeper2")
        check("状態を書けない環境でも落ちない", code == 0)

    print()
    if FAILURES:
        print(f"{len(FAILURES)}件が失敗しました: " + ", ".join(FAILURES))
        return 1
    print("すべて通りました。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
