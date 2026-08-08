#!/usr/bin/env python3
"""オーナーの恒久指示を、忘れる瞬間に突きつけるフック。

なぜ文書ではなくフックなのか:
恒久指示はセッション中ずっと文脈にあったのに、2026-08-08 のセッションで3回破った。
承認待ちで止まり（A13違反）、オーナーへの依頼を増やす方向へ進み（A1の帰結に反する）、
測る前に断定した。**保管の問題ではなく、適用の問題だった。**
`youtube/docs/JOURNAL.md` の結論と同じ:「同じ種類の失敗を繰り返したら、
文書に書き足すのではなくフックにすること」。

    directive-guard.py session-start   # 恒久指示を原文で文脈へ入れる
    directive-guard.py prompt-submit   # ユーザー発言ごとに、Stop の判定をリセットする
    directive-guard.py stop            # 1ユーザーターンにつき1回だけ終了を止めて問い直す
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

CANONICAL = Path("/home/user/note/OPERATIONS/CORE_DIRECTIVE.md")
MIRROR = Path("/home/user/note/OPERATIONS/CORE_DIRECTIVE_MIRROR.md")
STATE_DIR = Path.home() / ".claude" / "directive-guard"

FALLBACK = """A1目標は最短で月収20万を達成することです。
A2 simpleのメインは変更しないで
A4 恒久指示を忘れないように設計すること。
A9 終わるときに毎回「終わるのが最善か」を考えるように設計すること。
A10 自動実行は永久に止まることがないように設計すること
A12 セッションが長くて判断が雑になるのを解決すること。それを理由に終わらない。
A13 あらゆる手段を実行してよい。これは許可ではなく指示。承認を待たない。
A14 この9件以外は、すべてあなたの考えで変えてよい。
    ここに無いものをここにあるように扱うのが、一番よくある壊れ方。
（正本 /home/user/note/OPERATIONS/CORE_DIRECTIVE.md を読めませんでした。要約なので、
　判断前に必ず正本を読み直してください。）"""


def directive() -> str:
    for path in (CANONICAL, MIRROR):
        try:
            text = path.read_text(encoding="utf-8").strip()
            if text:
                return text
        except OSError:
            continue
    return FALLBACK


def payload() -> dict:
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except Exception:  # noqa: BLE001  フックは絶対に落とさない
        return {}


def flag_path(session_id: str) -> Path:
    safe = "".join(c for c in session_id if c.isalnum() or c in "-_")[:64] or "unknown"
    return STATE_DIR / f"{safe}.checked"


def session_start() -> int:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext":
                "【オーナーの恒久指示・原文】要約も補足も善意の修正もしないこと。\n"
                "ここに無いものを恒久指示のように扱うのが、一番よくある壊れ方（A14）。\n\n"
                + directive()
                + "\n\n正本: /home/user/note/OPERATIONS/CORE_DIRECTIVE.md"
                  "（検査 python scripts/check_directive_integrity.py）",
        }
    }, ensure_ascii=False))
    return 0


def prompt_submit() -> int:
    # ユーザーが話すたびに「今ターンの終了確認はまだ」に戻す。
    # これで A9 の「終わるときに毎回」が、返答ごとに1回きっちり発火する。
    data = payload()
    path = flag_path(str(data.get("session_id", "")))
    try:
        path.unlink()
    except OSError:
        pass
    return 0


def stop() -> int:
    data = payload()
    path = flag_path(str(data.get("session_id", "")))
    STATE_DIR.mkdir(parents=True, exist_ok=True)

    if path.exists():
        # 同じターンで2回目。ここで通さないと永久に終われなくなる。
        return 0

    try:
        path.write_text("1", encoding="utf-8")
    except OSError:
        return 0  # 記録できないなら止めない。デッドロックの方が害が大きい

    print(json.dumps({
        "decision": "block",
        "reason":
            "終了前の確認（A9）。次の4つに、記憶ではなく**実測と実施内容**で答えてから終えること。\n\n"
            "1. A9 いま終わるのが本当に最善か。まだ権限内でできる高価値作業はないか。\n"
            "2. A13 承認待ちで止まっていないか。「〜してよいですか」で終えようとしていないか。\n"
            "   これは許可ではなく指示。手段を狭く見積もらない。\n"
            "3. A1 オーナーへの依頼を増やしていないか。オーナーは指示を読むとは限らない。\n"
            "   最適化するのは依頼の読みやすさではなく**依頼の件数**。0件の経路を優先する。\n"
            "4. 測らずに「直した」「動いた」と書いていないか。書き込みは必ず読み直して確認する。\n"
            "5. **「あとで自動実行が拾うから」を終了の理由にしていないか。**\n"
            "   予定があることは、いま手を止める理由にならない（A1: 待っている時間も最短に含む）。\n"
            "   残量が理由なら、実測値を言えるか。言えないなら残量は理由ではない。\n"
            "6. **「無い」と言うとき、観測は1つで足りているか。**\n"
            "   2026-08-08、1つのAPI応答だけで「無い」と言って2回外した\n"
            "   （channels.list のリンク、list_triggers の毎時実行。どちらも実在した）。\n"
            "   不在の主張には独立した2つ目の観測を当てること。\n"
            "7. **報告に書いた識別子を、全部その目で読んだか。**\n"
            "   SHA・URL・ID・件数・パーセント。**思い出したものは書かない。**\n"
            "   2026-08-08、push の出力を `| tail -1` で受けて SHA を一度も見ずに\n"
            "   「Simple 4ba6d5c」と書いた。**存在しない番号だった**（実際は 9ed1ef2）。\n"
            "   中身は正しく届いていたので、読み直すまで誰も気づけない形だった。\n"
            "   push したら `git log origin/<branch> -1 --format=%h` を実行し、\n"
            "   **その出力を写すこと。** 推論ではなく捏造なので、これは別の失敗クラス。\n\n"
            "答えたうえで続ける価値があるなら続ける。無いならその理由を1行で述べて終える。\n"
            "（この確認は1ユーザーターンにつき1回だけ。次はそのまま終われる）",
    }, ensure_ascii=False))
    return 0


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "session-start":
        return session_start()
    if mode == "prompt-submit":
        return prompt_submit()
    if mode == "stop":
        return stop()
    print(f"unknown mode: {mode!r}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001  フックの失敗でセッションを壊さない
        print(f"directive-guard error: {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(0)
