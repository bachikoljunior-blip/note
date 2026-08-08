#!/usr/bin/env python3
"""OpenAI Assistants API の使用箇所を数えて、移行の見積りを出す（無料の診断）。

    python scan.py <path> [--json]

## なぜこれを作るか

2026-08-08 実測。OpenAI の公式 deprecations ページに、
**Assistants API の停止日は 2026-08-26** と書かれている（告知は 2025-08-26）。
公式の後継は Responses API ＋ Conversations API。

つまり **期限が硬く、残り日数が少なく、移行作業は機械的だが面倒** という需要が、
いま実在する。8か月0円だった4施策と違い、**こちらは需要が先にある。**

この診断は無料で配る。**数えるだけで、書き換えはしない。**
「何箇所あるか」「どの型の変換が必要か」が分かれば、
手でやるか道具を買うかを本人が決められる。

## 数え方（推測しない）

Assistants API の使用は、次の呼び出し形に現れる。SDK は言語ごとに違うので、
**呼び出しの綴りではなく、API のリソース名で数える。**

  beta.assistants     アシスタント定義      → Responses の prompt / instructions へ
  beta.threads        会話の器             → Conversations へ
  beta.threads.runs   実行                 → responses.create へ
  file_search / code_interpreter  ツール    → 対応する tools へ
  assistant_id / thread_id / run_id  識別子 → 保存済みIDの移行が要る

**行数ではなく箇所数を数える。** 1行に2つあれば2件。
コメント内も数える（消し忘れが移行漏れになるため）。ただし
`.git/`、`node_modules/`、`vendor/`、`dist/`、`build/` は見ない。
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", "vendor", "dist", "build", "__pycache__",
             ".venv", "venv", ".next", "target"}
SUFFIXES = {".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".rb", ".go",
            ".java", ".kt", ".cs", ".php", ".rs", ".ipynb", ".json", ".yaml", ".yml"}

# (キー, 正規表現, 移行先, 手作業の重さ)
# 重さは「1箇所を手で直すのにかかる分数」の目安。根拠のない精度は出さない。
PATTERNS: list[tuple[str, str, str, int]] = [
    ("assistants",      r"\bbeta\s*[.\[]\s*['\"]?assistants\b",
     "Responses API の instructions / prompt へ移す", 15),
    ("threads",         r"\bbeta\s*[.\[]\s*['\"]?threads\b",
     "Conversations API へ移す", 10),
    ("runs",            r"\b(?:threads\s*[.\[]\s*['\"]?runs|runs\s*[.\[]\s*['\"]?(?:create|poll|stream))\b",
     "responses.create（stream/poll 含む）へ移す", 20),
    ("assistant_id",    r"\bassistant_?[Ii]d\b",
     "保存済みアシスタントIDの持ち替えが要る", 5),
    ("thread_id",       r"\bthread_?[Ii]d\b",
     "保存済みスレッドIDを conversation へ持ち替える", 5),
    ("run_id",          r"\brun_?[Ii]d\b", "実行IDの扱いを responses へ合わせる", 5),
    ("file_search",     r"\bfile_search\b", "tools の file_search へ読み替える", 10),
    ("code_interpreter", r"\bcode_interpreter\b", "tools の code_interpreter へ読み替える", 10),
    ("message_create",  r"\bmessages\s*[.\[]\s*['\"]?create\b",
     "Conversations の items へ移す", 8),
]
COMPILED = [(k, re.compile(p), to, w) for k, p, to, w in PATTERNS]

SUNSET = "2026-08-26"
OFFICIAL = "https://developers.openai.com/api/docs/deprecations"


def walk(root: Path):
    if root.is_file():
        yield root
        return
    for p in root.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in SUFFIXES:
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        yield p


def scan(root: Path) -> dict:
    counts: dict[str, int] = {k: 0 for k, *_ in PATTERNS}
    hits: list[dict] = []
    files_touched: set[str] = set()

    for path in walk(root):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            for key, rx, to, _weight in COMPILED:
                found = rx.findall(line)
                if not found:
                    continue
                counts[key] += len(found)
                files_touched.add(str(path))
                if len(hits) < 500:  # 出力を膨らませない
                    hits.append({"file": str(path), "line": lineno,
                                 "kind": key, "migrate_to": to,
                                 "text": line.strip()[:160]})

    minutes = sum(counts[k] * w for k, _, _, w in PATTERNS)
    return {
        "sunset_date": SUNSET,
        "official_source": OFFICIAL,
        "scanned_root": str(root),
        "files_with_hits": len(files_touched),
        "counts": counts,
        "total_sites": sum(counts.values()),
        "manual_estimate_minutes": minutes,
        "hits": hits,
    }


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    root = Path(sys.argv[1])
    if not root.exists():
        print(f"見つかりません: {root}")
        return 1

    result = scan(root)
    if "--json" in sys.argv:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    print(f"OpenAI Assistants API 停止まで: {SUNSET}（公式: {OFFICIAL}）")
    print(f"調べた場所: {result['scanned_root']}")
    print()
    if not result["total_sites"]:
        print("該当箇所は見つかりませんでした。移行は不要と思われます。")
        print("※ 見ているのはソース内の呼び出しだけです。"
              "保存済みのアシスタントIDが外部DBにある場合は別途確認してください。")
        return 0

    print(f"該当 {result['total_sites']} 箇所 / {result['files_with_hits']} ファイル")
    print()
    print(f"{'種類':<18}{'箇所':>5}  移行先")
    for key, _, to, _w in PATTERNS:
        n = result["counts"][key]
        if n:
            print(f"{key:<18}{n:>5}  {to}")
    est = result["manual_estimate_minutes"]
    print()
    print(f"手作業の目安: 約 {est} 分（{est/60:.1f} 時間）")
    print("※ 1箇所あたりの分数は目安です。**実測値ではありません。**"
          "分岐やテストの量で大きく変わります。")
    print()
    print("最初に見る箇所:")
    for h in result["hits"][:10]:
        print(f"  {h['file']}:{h['line']}  [{h['kind']}]  {h['text'][:80]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
