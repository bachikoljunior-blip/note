#!/usr/bin/env python3
"""Assistants API から Responses / Conversations API への機械的な書き換え（有料側の中身）。

    python codemod.py <path> --dry-run       # 変更案だけ出す（既定）
    python codemod.py <path> --apply         # 実際に書き換える（.bak を残す）
    python codemod.py <path> --json

## 何をして、何をしないか

**する**: 綴りが1対1で決まる置き換えと、後始末が要る箇所の指摘。
**しない**: 意味の変わる書き換え。判断が要るものは触らず、印を付けて人に返す。

これは大事な線引きで、勝手に直すと**壊れたことに気づけない**。
`scan.py`（無料の診断）が「どこが何箇所か」、この codemod が「機械的に直せる分」、
残りは `MIGRATION.md` の手順で人が直す、という分担にしてある。

## 1対1で決まるもの

  client.beta.assistants.create(...)   → 保存せず instructions として持つ形へ（要手当）
  client.beta.threads.create()         → client.conversations.create()
  client.beta.threads.messages.create  → client.conversations.items.create
  client.beta.threads.runs.create      → client.responses.create
  thread_id=                           → conversation=
  assistant_id=                        → （instructions/prompt へ。機械では消せない）

## 触らないもの（印だけ付ける）

- `runs.poll` / `runs.stream` の待ち合わせ —— Responses は返り方が違うので、
  待ち方そのものを書き直す必要がある
- `file_search` / `code_interpreter` の vector store 周り
- 保存済みの assistant_id / thread_id をDBに持っている場合の移行

**「たぶん動く」書き換えを混ぜないこと。** 停止日は 2026-08-26 で、
壊れたまま気づかない方が、直っていないより高くつく。
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", "vendor", "dist", "build", "__pycache__",
             ".venv", "venv", ".next", "target"}
SUFFIXES = {".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx"}

# (説明, 検索, 置換)  —— 意味が変わらないものだけ
REWRITES: list[tuple[str, re.Pattern[str], str]] = [
    ("threads.messages.create → conversations.items.create",
     re.compile(r"\bbeta\.threads\.messages\.create\b"), "conversations.items.create"),
    ("threads.runs.create → responses.create",
     re.compile(r"\bbeta\.threads\.runs\.create\b"), "responses.create"),
    ("threads.create → conversations.create",
     re.compile(r"\bbeta\.threads\.create\b"), "conversations.create"),
    ("threads.retrieve → conversations.retrieve",
     re.compile(r"\bbeta\.threads\.retrieve\b"), "conversations.retrieve"),
    ("threads.del → conversations.delete",
     re.compile(r"\bbeta\.threads\.del(?:ete)?\b"), "conversations.delete"),
    ("thread_id= → conversation=",
     re.compile(r"\bthread_id\s*="), "conversation="),
    ("threadId: → conversation:",
     re.compile(r"\bthreadId\s*:"), "conversation:"),
]

# (説明, 検索, なぜ機械では直せないか)
FLAGS: list[tuple[str, re.Pattern[str], str]] = [
    ("runs.poll / runs.stream", re.compile(r"\bruns\.(?:poll|stream|createAndPoll|create_and_poll)\b"),
     "Responses は返り方が違う。待ち合わせの書き方そのものを直す必要がある"),
    ("assistants.create/retrieve", re.compile(r"\bbeta\.assistants\.(?:create|retrieve|update|list)\b"),
     "アシスタントという保存物が無くなる。instructions か prompt として持ち直すので、"
     "設計の判断が要る"),
    ("assistant_id", re.compile(r"\bassistant_?[Ii]d\b"),
     "保存済みIDが残っている場所（DB・設定）を人が洗い出す必要がある"),
    ("vector store / file_search", re.compile(r"\b(?:vector_stores?|file_search)\b"),
     "vector store の紐づけ方が変わる。ファイルの再登録が要る場合がある"),
    ("code_interpreter", re.compile(r"\bcode_interpreter\b"),
     "tools の指定方法を読み替える。実行結果の取り出し方も変わる"),
]


def walk(root: Path):
    if root.is_file():
        yield root
        return
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in SUFFIXES \
                and not any(part in SKIP_DIRS for part in p.parts):
            yield p


def process(root: Path, apply: bool) -> dict:
    changed_files: list[dict] = []
    flagged: list[dict] = []
    total_rewrites = 0

    for path in walk(root):
        try:
            original = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        text = original
        per_file: dict[str, int] = {}
        for label, rx, repl in REWRITES:
            text, n = rx.subn(repl, text)
            if n:
                per_file[label] = per_file.get(label, 0) + n
                total_rewrites += n

        for lineno, line in enumerate(original.splitlines(), 1):
            for label, rx, why in FLAGS:
                if rx.search(line):
                    flagged.append({"file": str(path), "line": lineno,
                                    "kind": label, "why": why,
                                    "text": line.strip()[:140]})

        if per_file:
            changed_files.append({"file": str(path), "rewrites": per_file})
            if apply:
                path.with_suffix(path.suffix + ".bak").write_text(original, encoding="utf-8")
                path.write_text(text, encoding="utf-8")

    return {
        "applied": apply,
        "rewritten_sites": total_rewrites,
        "changed_files": changed_files,
        "needs_human": flagged,
        "sunset_date": "2026-08-26",
    }


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    root = Path(sys.argv[1])
    if not root.exists():
        print(f"見つかりません: {root}")
        return 1
    apply = "--apply" in sys.argv
    result = process(root, apply)

    if "--json" in sys.argv:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    mode = "書き換えました（.bak を残しています）" if apply else "変更案です（--apply で実行）"
    print(f"機械的に直せる箇所: {result['rewritten_sites']} —— {mode}")
    for c in result["changed_files"]:
        print(f"  {c['file']}")
        for label, n in c["rewrites"].items():
            print(f"      {n:>3}  {label}")
    print()
    print(f"人が判断する箇所: {len(result['needs_human'])}")
    seen: set[str] = set()
    for f in result["needs_human"]:
        if f["kind"] in seen:
            continue
        seen.add(f["kind"])
        print(f"  [{f['kind']}] {f['why']}")
    print()
    print("**機械が直した分だけでは動きません。** 上の箇所を必ず人が確認してください。")
    print("停止日 2026-08-26（https://developers.openai.com/api/docs/deprecations）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
