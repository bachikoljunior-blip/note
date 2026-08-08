#!/usr/bin/env python3
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from codemod import process
from scan import scan

USING = {
    "app.py": (
        "from openai import OpenAI\nclient = OpenAI()\n"
        "empty = client.beta.threads.create()\n"
        'seeded = client.beta.threads.create(messages=[{"role": "user", "content": "hi"}])\n'
        'a = client.beta.assistants.create(name="h", tools=[{"type": "file_search"}])\n'
        'client.beta.threads.messages.create(thread_id=empty.id, role="user", content="x")\n'
        "run = client.beta.threads.runs.create(thread_id=empty.id, assistant_id=a.id)\n"
    ),
    "app.ts": (
        "const asst = await client.beta.assistants.retrieve(assistantId);\n"
        "const thread = await client.beta.threads.create();\n"
        "const r = await client.beta.threads.runs.stream({ threadId: thread.id });\n"
    ),
}

MIGRATED = {
    "clean.py": (
        "from openai import OpenAI\nclient = OpenAI()\n"
        'r = client.responses.create(model="gpt-5", input="hello")\n'
        "c = client.conversations.create()\n"
    ),
    "threading_use.py": "import threading\nt = threading.Thread(target=work)\n",
}


def write(root: Path, files: dict[str, str]) -> Path:
    for name, body in files.items():
        (root / name).write_text(body, encoding="utf-8")
    return root


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        result = scan(write(Path(directory), USING))
        assert result["total_sites"] > 0
        for key in ("assistants", "threads", "runs", "file_search"):
            assert result["counts"][key] > 0, key

    with tempfile.TemporaryDirectory() as directory:
        assert scan(write(Path(directory), MIGRATED))["total_sites"] == 0

    with tempfile.TemporaryDirectory() as directory:
        root = write(Path(directory), USING)
        original = (root / "app.py").read_text(encoding="utf-8")
        preview = process(root, apply=False)
        assert preview["rewritten_sites"] == 2
        assert any("conversations.create()" in item["diff"] for item in preview["changed_files"])
        assert (root / "app.py").read_text(encoding="utf-8") == original

        result = process(root, apply=True)
        body = (root / "app.py").read_text(encoding="utf-8")
        assert result["rewritten_sites"] == 2
        assert "client.conversations.create()" in body
        assert "beta.threads.create(messages=" in body
        assert "beta.threads.messages.create" in body
        assert "beta.threads.runs.create" in body
        assert "assistant_id" in body
        assert (root / "app.py.bak").read_text(encoding="utf-8") == original
        kinds = {item["kind"] for item in result["needs_human"]}
        assert {"thread with initial messages", "thread messages", "runs", "assistant configuration"} <= kinds
        assert process(root, apply=False)["rewritten_sites"] == 0

    print("scanner and conservative codemod tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
