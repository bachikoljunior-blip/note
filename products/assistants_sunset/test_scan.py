#!/usr/bin/env python3
"""scan.py が、当てるべきものを当て、当ててはいけないものを当てないか試す。

**当たることの確認だけでは足りない。** 全部に反応する正規表現でも「当たる」ので、
移行済みのコードに 0 を返すことを同じ強さで確かめる。

    python products/assistants_sunset/test_scan.py
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scan import scan  # noqa: E402

USING = {
    "app.py": (
        "from openai import OpenAI\n"
        "client = OpenAI()\n"
        'a = client.beta.assistants.create(name="h", tools=[{"type": "file_search"}])\n'
        "t = client.beta.threads.create()\n"
        'client.beta.threads.messages.create(thread_id=t.id, role="user", content="x")\n'
        "run = client.beta.threads.runs.create(thread_id=t.id, assistant_id=a.id)\n"
    ),
    "app.ts": (
        "const asst = await client.beta.assistants.retrieve(assistantId);\n"
        "const thread = await client.beta.threads.create();\n"
        "const r = await client.beta.threads.runs.stream({ threadId: thread.id });\n"
    ),
}

MIGRATED = {
    # 移行後のコード。ここに反応したら誤検出。
    "clean.py": (
        "from openai import OpenAI\n"
        "client = OpenAI()\n"
        'r = client.responses.create(model="gpt-5", input="hello")\n'
        'c = client.conversations.create()\n'
    ),
    # 紛らわしいが無関係なもの。thread は普通の英単語として頻出する。
    "threading_use.py": (
        "import threading\n"
        "t = threading.Thread(target=work)\n"
        "t.start()\n"
        "# this runs in a background thread\n"
    ),
}


def write(tmp: Path, files: dict) -> Path:
    for name, body in files.items():
        (tmp / name).write_text(body, encoding="utf-8")
    return tmp


def main() -> int:
    failures: list[str] = []

    with tempfile.TemporaryDirectory() as d:
        r = scan(write(Path(d), USING))
        if r["total_sites"] == 0:
            failures.append("Assistants API を使っているのに 0 件だった")
        else:
            print(f"  ok  使用中のコードを検出（{r['total_sites']}箇所 / "
                  f"{r['files_with_hits']}ファイル）")
        for key in ("assistants", "threads", "runs", "file_search"):
            if r["counts"].get(key, 0) == 0:
                failures.append(f"{key} を検出できていない")
        if r["manual_estimate_minutes"] <= 0:
            failures.append("手作業の見積りが 0 以下")

    with tempfile.TemporaryDirectory() as d:
        r = scan(write(Path(d), MIGRATED))
        if r["total_sites"] != 0:
            failures.append(
                f"移行済み・無関係コードに誤検出した（{r['total_sites']}件）: "
                f"{[h['text'] for h in r['hits'][:3]]}")
        else:
            print("  ok  移行済みコードと threading には反応しない")

    # codemod: 1対1で決まるものだけ直し、判断が要るものは触らないこと。
    # ここが逆だと「たぶん動く」書き換えが混ざり、壊れたことに気づけなくなる。
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from codemod import process  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as d:
        tmp = write(Path(d), {"app.py": USING["app.py"]})
        r = process(tmp, apply=True)
        body = (tmp / "app.py").read_text(encoding="utf-8")
        if r["rewritten_sites"] == 0:
            failures.append("codemod が1件も書き換えなかった")
        for gone in ("beta.threads.create", "beta.threads.runs.create", "thread_id="):
            if gone in body:
                failures.append(f"codemod が {gone} を残した")
        for kept in ("beta.assistants.create", "assistant_id"):
            if kept not in body:
                failures.append(
                    f"codemod が {kept} を勝手に書き換えた。**判断が要る箇所は触ってはいけない**")
        if not (tmp / "app.py.bak").is_file():
            failures.append("codemod が .bak を残していない")
        if not r["needs_human"]:
            failures.append("codemod が『人が判断する箇所』を1件も挙げなかった")
        if not failures:
            print(f"  ok  codemod は機械的な{r['rewritten_sites']}箇所だけ直し、"
                  f"判断が要る{len(r['needs_human'])}箇所は残した")

    print()
    if failures:
        for f in failures:
            print("NG  " + f)
        return 1
    print("すべて通過")
    return 0


if __name__ == "__main__":
    sys.exit(main())
