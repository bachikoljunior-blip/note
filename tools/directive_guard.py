#!/usr/bin/env python3
"""Keep the exact current permanent directive in context and review every yield once."""
from __future__ import annotations

import base64
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(os.environ.get("REVENUE_REPO_ROOT", "/home/user/note"))
CANONICAL = ROOT / "OPERATIONS" / "CORE_DIRECTIVE.md"
MIRROR = ROOT / "OPERATIONS" / "CORE_DIRECTIVE_MIRROR.md"
ENCODED = ROOT / "OPERATIONS" / "CORE_DIRECTIVE.b64"
STATE_DIR = Path.home() / ".claude" / "directive-guard"
FALLBACK = "あらゆる手段を尽くし、月収20万円を最短で達成してください。あらゆる手段を尽くす前提で、月収20万円を達成するまでどれくらいかかるか予測し、予測がいくらかかっても達成できないになる場合は、予測が達成可能になるまで考えてください。月収20万円を達成し、その後維持することが確認されるまで、予測が短くなるように行動し続け、あなたの実行が永久に止まることがない設計を保証してください。私への操作依頼は最小になっているか確認し、最小にしてください。週一回以上、私が操作依頼を達成できる前提で考えてください。最低週一回です。また、使用量を考慮し、毎回最新の使用量を取得して考慮するようにしてください。操作依頼とは別に私への指示を出してもいいです。\nどれだけセッションが長くなってもこのメッセージの最初から最後までと全く同じ指示に永久に従わなくなることがないように設計を保証してください。設計の保証ができないと判断した場合、できない理由を完全に潰してください。\n以上にないものは、最短で月収20万円を達成するためにあなたが自由に改変していいです。"


def directive() -> str:
    for path in (CANONICAL, MIRROR):
        try:
            value = path.read_text(encoding="utf-8").strip()
            if value:
                return value
        except OSError:
            continue
    try:
        value = base64.b64decode(
            b"".join(ENCODED.read_bytes().split()), validate=True
        ).decode("utf-8").strip()
        if value:
            return value
    except Exception:  # noqa: BLE001
        pass
    return FALLBACK


def payload() -> dict:
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except Exception:  # noqa: BLE001
        return {}


def flag_path(session_id: str) -> Path:
    safe = "".join(c for c in session_id if c.isalnum() or c in "-_")[:64] or "unknown"
    return STATE_DIR / "{}.checked".format(safe)


def session_start() -> int:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext":
                "【ユーザー恒久指示・原文】要約・補足・旧版の混入を禁止する。\n"
                "以下の原文だけを恒久指示として扱う。\n\n"
                + directive()
                + "\n\n正本: OPERATIONS/CORE_DIRECTIVE.md"
                  "（検査: python scripts/check_directive_integrity.py）",
        }
    }, ensure_ascii=False))
    return 0


def prompt_submit() -> int:
    path = flag_path(str(payload().get("session_id", "")))
    try:
        path.unlink()
    except OSError:
        pass
    return 0


def stop() -> int:
    path = flag_path(str(payload().get("session_id", "")))
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return 0
    try:
        path.write_text("1", encoding="utf-8")
    except OSError:
        return 0

    remaining = ""
    try:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "check_before_ending.py")],
            capture_output=True, text=True, timeout=90,
        )
        if proc.stdout.strip():
            remaining = (
                "\n\n── 機械が数えた実測（scripts/check_before_ending.py）──\n"
                + proc.stdout.rstrip()
            )
    except Exception as exc:  # noqa: BLE001
        remaining = "\n\n（残作業の検査を実行できなかった: {}）".format(exc)

    reason = (
        "終了前の確認。次を、記憶ではなく実測と実施内容で確認してからyieldすること。\n\n"
        "1. 正本・ミラー・バックアップとmanifestが、最新の恒久指示原文に完全一致しているか。\n"
        "2. 月収20万円の到達予測を今この回で短縮できる、安全かつ権限内の高価値作業が残っていないか。\n"
        "3. 本人操作を0件から検討し、残る操作を週次の単一セッションへ最小化したか。\n"
        "4. 最新使用量を取得時刻・鮮度・リセット時刻とともに取得し、配分へ反映したか。\n"
        "5. 売上・給与・契約・公開・送信・実行をread-backせず、達成済みと断定していないか。\n"
        "6. 主実行と監視の継続を確認し、次回が再開できる状態・次の発火条件を外部正本へ保存したか。\n\n"
        "続ける価値があるなら続ける。現時点で安全に実行可能な単位が無い場合だけ、"
        "根拠と次の自動発火条件を記録してyieldする。"
        "\n（この確認は1ユーザーターンにつき1回だけ。次はそのまま終われる）"
        + remaining
    )
    print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))
    return 0


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "session-start":
        return session_start()
    if mode == "prompt-submit":
        return prompt_submit()
    if mode == "stop":
        return stop()
    print("unknown mode: {!r}".format(mode), file=sys.stderr)
    return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001
        print("directive-guard error: {}: {}".format(type(exc).__name__, exc), file=sys.stderr)
        sys.exit(0)
